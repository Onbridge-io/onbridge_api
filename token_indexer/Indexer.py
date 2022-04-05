import json
import os
import time
from typing import Union

import django
import requests
import web3.contract
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.types import Address, ChecksumAddress
from app import settings
from datetime import datetime
import logging

log = logging.getLogger(__name__)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

STEP = 1000


class IndexerException(Exception):
    pass


class Indexer:
    """
    Indexer class to check events in blockchain
    Main concept:
    1) Initialization stage (def __init__): executed one time on starting indexer. It takes all necessary data from envs
    setups all necessary objects and gives all data to logs
    2) Main cycle (def main_cycle): this part of indexer is started outside the class. It is the startpoint for indexer.
    It also handles all IndexerException situations
    3) Cycle body (def cycle_body): here the logic of indexer is being executed.

    All other methods are executed inside cycle body.
    """

    def get_contract_by_address_and_abi(self, address: Union[Address, ChecksumAddress],
                                     abi_file_name: str) -> web3.contract.Contract:
        """
        Methods obtains a Contract object from address and ABI filename
        """
        with open(abi_file_name, 'r') as f:
            data = json.load(f)
        return self.w3.eth.contract(abi=data['abi'], address=address)

    def get_token_metadata_from_contract(self, token_id: int) -> dict:
        """
        Receive metadata (dict with token info: image, params, etc.)
        It consists of 3 stages:
        1) Go to contract method tokenURI(uint256 tokenId) and get uri for file with metadata
        2) Go to received in step (1) uri and get JSON file
        3) Convert JSON file contents to dict and return it
        If on step (1) or (2) there is a failure, IndexerException is raised
        """
        try:
            token_uri: str = self.token_contract.functions.tokenURI(token_id).call()
            log.info(f"    Receiving metadata: Received for token_id: {token_id} tokenURI: {token_uri}.")
        except Exception as e:
            log.error(f"    Receiving metadata: ERROR: Attempted to get tokenURI from contract for token_id={token_id}"
                      f" at chain_id={self.chain_id}, but caught an error: {e}")
            raise IndexerException(f"Exception {e} while receiving tokenURI for token_id={token_id}")
        try:
            token_metadata: dict = requests.get(token_uri, timeout=120).json()
            log.info(f"    Receiving metadata: Received following metadata entries: {token_metadata.keys()}")
            return token_metadata
        except Exception as e:
            log.error(f"    Receiving metadata: ERROR: Attempted to download metadata, caught error {e}."
                      f" Seems like restarting indexer must be enough to solve this.")
            raise IndexerException(f"Exception {e} while receiving metadata for token "
                                   f"with token_id={token_id} at uri: {token_uri}. "
                                   f"It may be caused by problem with IPFS provider")

    def index_new_token(self, event):
        """
        Main method of writing data to database.
        If the token is new it is created and stored in DB.
        Otherwise, it will be updated with data from event
        """
        empty_string = ''
        token_id = event.args.tokenId
        try:
            token = self.token_model.objects.get(token_id=token_id)
            log.info(f"  Index new token: token with  token_id={token_id} already exists")
        except self.token_model.DoesNotExist:
            log.info(f"  Index new token: Token with token_id={token_id} does not exist. Creating new one")
            token = self.token_model(token_id=token_id)
            token_metadata = self.get_token_metadata_from_contract(token_id)
            if image_uri_from_metadata := token_metadata.get('image'):
                log.info(f"  Index new token: Metadata contains image uri, removing https://ipfs.io/ipfs/ from this:"
                         f" {image_uri_from_metadata}")
                token.ipfs_uri_image = image_uri_from_metadata.replace("https://ipfs.io/ipfs/", "")
                token.image = token.ipfs_uri_image
            else:
                log.info("  Index new token: Metadata does not contain image uri, providing empty string")
                token.ipfs_uri_image = empty_string

        self.update_token_data(event, token)

        if not os.path.isfile(token.image.url[1:]):
            log.info(f"  Index new token: no picture is provided, expected file: {token.image.url[1:]}. Fetching")
            self.fetch_image(token)
        else:
            log.info(f"  Index new token: the picture for token_id {token.token_id} has already been downloaded")

    def handle_bridge_events(self, direction, event_name, _from_block, _to_block):
        events = getattr(
                self.bridge_contract.events, event_name
            ).createFilter(fromBlock=_from_block, toBlock=_to_block).get_all_entries()

        log.info(f"  Found {len(events)} events {event_name}")
        """
        AttributeDict({
            'args': AttributeDict(
                {
                    'l1Token': '0xe6847645B1832B2923e5938ec482f2b0EfA6DE4c', 
                    '_from': '0x5fCb8f7149E8aD03544157C90E6f81b26933d3a2', 
                    '_to': '0x5fCb8f7149E8aD03544157C90E6f81b26933d3a2', 
                    '_amount': 0
                }
            ), 
            'event': 'DepositInitiated', 
            'logIndex': 9, 
            'transactionIndex': 3, 
            'transactionHash': HexBytes('0x38a962089e36c869802d408b59ce9bf3ba1780d504ee4a4dd5ea6d36a49e95bb'), 
            'address': '0x099e3307be3b694e8C7dBc54E2ecB8897806BD2A', 
            'blockHash': HexBytes('0x1a24282f2af5d451dcf8c339b3e6b91a04df339d9d6a785788573a79ddc6e52d'), 
            'blockNumber': 16780832
        })
        """
        for event in events:
            token = self.token_model.objects.get(token_id=event.args._amount)
            self.action_model.objects.create(
                token=token,
                direction=direction,
                status=self.action_model.Status.NEW,
                bridge_sender=event.address,
                l1_tx=event.transactionHash.hex()
            )
            log.info(f"    Event {event_name} with transaction {event.transactionHash.hex()} processed")

    def update_token_data(self, event, token):
        """
        Write data to token from event and save
        """
        timestamp_from_block = self.w3.eth.get_block(event.blockNumber)['timestamp']
        timestamp_from_database = token.blockchain_timestamp
        if timestamp_from_database is None:
            log.info(f"    Update token: It is the very first time when token "
                     f"with token id = {token.token_id} is being written")
            timestamp_from_database = 0
        if timestamp_from_database < timestamp_from_block:
            log.info(f"    Update token: Database contained old data for token: {token}. ")
            log.info(f"    Update token: Last update time stored in db is: "
                     f"{datetime.fromtimestamp(timestamp_from_database)}")
            log.info(f"    Update token: Current block time is {datetime.fromtimestamp(timestamp_from_block)}")
            if self.chain_id != token.chain_id and token.chain_id is not None:
                log.info(
                    f"    Update token: token has been relocated from chain {token.chain_id} to {self.chain_id}")
            token.owner = event.args.to
            token.chain_id = self.chain_id
            token.tx = event.transactionHash.hex()
            token.block_number = event.blockNumber
            token.blockchain_timestamp = timestamp_from_block
            token.save()
            log.info(f"    Update token: Now database contains new data for token: {token}")

    def fetch_image(self, token):
        """
        Retrieve image from IPFS
        If IPFS provider will give response code different from 200 OK, IndexerException will be raised
        """
        log.info(f"    Fetching image: download image for token_id {token.token_id}")
        uri = f"{self.ipfs_host}{''.join(['/ipfs/', token.ipfs_uri_image])}"
        log.info(f"    Fetching image: send IPFS system GET query at {uri}")
        response = requests.get(uri, timeout=120)

        if response.status_code == 200:
            log.info(f"    Fetching image: IPFS system response: {response.status_code} {response.reason}")
            data = response.content
            _, __, subdir_name, file_name = token.image.url.split("/")
            subdir = os.path.join(self.storage_media, subdir_name)
            if not os.path.exists(subdir) and not os.path.isdir(subdir):
                os.mkdir(os.path.join(subdir))
            file = os.path.join(subdir, file_name)
            with open(file, "wb") as f:
                f.write(data)
            log.info(f"    Fetching image: image downloaded. path: {file}.")
        else:
            log.error("    Fetching image: image NOT loaded.")
            raise IndexerException(f"While fetching image HTTP error occurred: "
                                   f"received status code {response.status_code} {response}")

    def __init__(
            self,
            upstream: str,
            token_address: str,
            bridge_address: str,
            token_abi_filename: str,
            bridge_abi_filename: str,
            indexer_interval: int,
            ipfs_host: str
    ):
        """
        Here all indexer fields are configured
        """
        django.setup()
        self.storage_media = settings.MEDIA_ROOT
        log.info(f"Init stage: storage media path is {self.storage_media}")
        from onbridge.models import Indexer, Token, ActionBridge
        self.indexer_model = Indexer
        self.token_model = Token
        self.action_model = ActionBridge

        self.indexer_interval = indexer_interval
        log.info(f"Init stage: indexer interval is {self.indexer_interval} s")

        self.ipfs_host = ipfs_host
        log.info(f"Init stage: ipfs host is {self.ipfs_host}")

        self.w3 = Web3(Web3.HTTPProvider(upstream, request_kwargs={'timeout': 120}))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        self.chain_id = self.w3.eth.chain_id
        log.info(f"Init stage: chain id is {self.chain_id}")

        self.bridge_address = self.w3.toChecksumAddress(bridge_address)
        log.info(f"Init stage: bridge contract address is {self.bridge_address}")

        self.token_address = self.w3.toChecksumAddress(token_address)
        log.info(f"Init stage: token contract address is {self.token_address}")

        self.token_contract = self.get_contract_by_address_and_abi(self.token_address, token_abi_filename)
        log.info(f"Init stage: successfully created token contract. Ready to start")

        self.bridge_contract = self.get_contract_by_address_and_abi(self.bridge_address, bridge_abi_filename)
        log.info(f"Init stage: successfully created bridge contract. Ready to start")

    def main_cycle(self):
        """
        Main cycle of indexer
        If there's IndexerException caught, indexer will be shut down with status code 1
        """
        try:
            while True:
                self.main_cycle_body()
                log.info(f"Cycle end: yet another cycle is passed. Sleeping for {self.indexer_interval} seconds")
                time.sleep(self.indexer_interval)
        except IndexerException as e:
            log.error(f"Shutting down indexer because error occurred: {e}")
            exit(1)

    def main_cycle_body(self):
        """
        Main cycle body where events are filtered by block
        """
        indexer = self.indexer_model.objects.get(chain_id=self.chain_id)
        first_block = indexer.indexed_block
        log.info(f"Cycle body: obtained first block from database: {first_block}")
        last_block = self.w3.eth.get_block('latest')['number']
        log.info(f"Cycle body: obtained last block from blockchain: {last_block}")
        log.info(f"Cycle body: start index process from {first_block} block to {last_block}...")

        for from_block in range(first_block, last_block, STEP):
            log.info("Cycle body: sleep...")
            time.sleep(self.indexer_interval)
            log.info(f"Cycle body: current index block: {from_block}")

            log.info("Event Transfer Handling")
            to_block = from_block + STEP
            event_transfer = self.token_contract.events.Transfer.createFilter(
                fromBlock=from_block,
                toBlock=to_block
            )
            events = event_transfer.get_all_entries()
            log.info(f"Cycle body: obtained {len(events)} events")
            for event in events:
                if event.args.to == self.bridge_address \
                        or event.args.to == '0x0000000000000000000000000000000000000000':
                    log.info(
                        f"Cycle body: token id {event.args.tokenId} is on bridge: {self.bridge_address}. "
                        f"Seems token is being burned or transferred to another chain")
                    continue
                else:
                    log.info(f"Cycle body: token id {event.args.tokenId} "
                             f"is taken from {event.args['from']} to {event.args.to}")

                    self.index_new_token(event)

            log.info("Event Bridge Handling")
            if self.chain_id == 97:
                log.info('The current network is type L1')
                self.handle_bridge_events(
                    self.action_model.Direction.DEPOSIT,
                    'DepositInitiated',
                    from_block,
                    to_block
                )
            else:
                log.info('The current network is type L2')
                self.handle_bridge_events(
                    self.action_model.Direction.WITHDRAW,
                    'WithdrawalInitiated',
                    from_block,
                    to_block
                )

            indexer.indexed_block = last_block + 1 if to_block > last_block else to_block + 1
            indexer.save()
            log.info(f"Cycle body: next block number: {indexer.indexed_block}")

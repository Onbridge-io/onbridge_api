import io
import json
import logging
import os
import time

import django
import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from web3 import Web3
from web3.middleware import geth_poa_middleware

log = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

UPSTREAM = os.environ['UPSTREAM']
TOKEN_ADDRESS = os.environ['TOKEN_ADDRESS']
TOKEN_ABI_FILENAME = os.environ['TOKEN_ABI_FILENAME']
BRIDGE_ADDRESS = os.environ['BRIDGE_ADDRESS']
INDEXER_INTERVAL = int(os.environ['INDEXER_INTERVAL'])
IPFS_HOST = os.environ["IPFS_HOST"]

STEP = 1000


def init_token(w3, address, abi_file_name):
    with open(abi_file_name, 'r') as f:
        data = json.load(f)
    return w3.eth.contract(abi=data['abi'], address=address)


def indexing_new_token(token_contract, chain_id, event):
    empty_string = ''
    token_id = event.args.tokenId
    try:
        token = Token.objects.get(token_id=token_id)
    except ObjectDoesNotExist:
        token = Token(token_id=token_id)

        token_uri = token_contract.functions.tokenURI(token_id).call()
        token_metadata = requests.get(token_uri, timeout=120).json()
        token.ipfs_uri_image = token_metadata['image'].replace("https://ipfs.io/ipfs/", "") \
            if token_metadata.get('image') else empty_string

        if token.ipfs_uri_image:
            token.image = token.ipfs_uri_image

    token.owner = event.args.to
    token.chain_id = chain_id
    token.tx = event.transactionHash.hex()
    token.block_number = event.blockNumber

    token.save()
    log.info(f'token id {token_id} save to db')
    if not os.path.isfile(token.image.url[1:]):
        fetch_image(token, storage_media)
    else:
        log.info("the picture for token_id {} has already been downloaded".format(token.token_id))

def fetch_image(token, storage_media):
    ipfs_host = IPFS_HOST + '{}'
    log.info("download image for token_id {}".format(token.token_id))

    uri = ipfs_host.format("".join(["/ipfs/", token.ipfs_uri_image]))
    log.info("requests: GET {}".format(uri))
    response = requests.get(uri, timeout=120)

    if response.status_code == 200:
        log.info("{} {}".format(response.status_code, response.reason))
        data = response.content
        _, __, subdir_name, file_name = token.image.url.split("/")
        subdir = os.path.join(storage_media, subdir_name)
        if not os.path.exists(subdir) and not os.path.isdir(subdir):
            os.mkdir(os.path.join(subdir))
        file = os.path.join(subdir, file_name)
        with open(file, "wb") as f:
            f.write(data)
        log.info("image downloaded. path: {}.".format(file))
    else:
        log.error("image NOT loaded.")
        raise Exception("{} {}".format(response.status_code, response.reason))


if __name__ == '__main__':
    django.setup()
    storage_media = settings.MEDIA_ROOT
    from onbridge.models import Status, Token

    w3 = Web3(Web3.HTTPProvider(UPSTREAM, request_kwargs={'timeout': 120}))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    chain_id = w3.eth.chain_id
    bridge_address = w3.toChecksumAddress(BRIDGE_ADDRESS)
    token_contract = init_token(w3, TOKEN_ADDRESS, TOKEN_ABI_FILENAME)

    while True:
        status = Status.objects.get(chain_id=chain_id)
        first_block = status.indexed_block

        last_block = w3.eth.get_block('latest')['number']
        log.info(f'start indexing process from {first_block} block to {last_block}...')

        for block_number in range(first_block, last_block, STEP):
            log.info('sleep...')
            time.sleep(INDEXER_INTERVAL)
            log.info(f'current indexing block: {block_number}')

            event_transfer = token_contract.events.Transfer.createFilter(
                fromBlock=block_number,
                toBlock=block_number + STEP
            )
            events = event_transfer.get_all_entries()

            for event in events:
                if event.args.to == bridge_address or event.args.to == '0x0000000000000000000000000000000000000000':
                    log.info(f'token id {event.args.tokenId} on bridge: {bridge_address}')
                    continue

                indexing_new_token(token_contract, chain_id, event)

            status.indexed_block = last_block + 1 if block_number + STEP > last_block else block_number + STEP + 1
            status.save()
            log.info(f'next block number: {status.indexed_block}')

        log.info('done, pause...')
        time.sleep(INDEXER_INTERVAL)

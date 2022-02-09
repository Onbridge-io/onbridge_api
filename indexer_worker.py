import io
import json
import logging
import os
import time

import django
import requests
from django.conf import settings
from django.core.files.images import ImageFile
from web3 import Web3
from web3.middleware import geth_poa_middleware

log = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

UPSTREAM = os.environ['UPSTREAM']
TOKEN_ADDRESS = os.environ['TOKEN_ADDRESS']
TOKEN_ABI_FILENAME = os.environ['TOKEN_ABI_FILENAME']
BRIDGE_ADDRESS = os.environ['BRIDGE_ADDRESS']

STEP = 1000


def init_token(w3, address, abi_file_name):
    with open(abi_file_name, 'r') as f:
        data = json.load(f)
    return w3.eth.contract(abi=data['abi'], address=address)


def indexing_new_token(token_contract, token_id, chain_id, event):
    token_uri = token_contract.functions.tokenURI(token_id).call()
    token_metadata = requests.get(token_uri, timeout=120).json()
    token_image_url = token_metadata['image']
    image_bytes = requests.get(token_image_url, timeout=120).content
    token_image = ImageFile(io.BytesIO(image_bytes), name=f'{token_id}.png')

    Token.objects.get_or_create(
        token_id=token_id,
        defaults={
            'owner': event.args.to,
            'chain_id': chain_id,
            'tx': event.transactionHash.hex(),
            'block_number': event.blockNumber,
            'image': token_image
        })

    log.info(f'token id {token_id} save to db')


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
            time.sleep(1)
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

                indexing_new_token(token_contract, event.args.tokenId, chain_id, event)

            status.indexed_block = last_block + 1 if block_number + STEP > last_block else block_number + STEP + 1
            status.save()
            log.info(f'next block number: {status.indexed_block}')

        log.info('done, pause...')
        time.sleep(1)

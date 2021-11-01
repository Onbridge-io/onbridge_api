import os
import logging
import time
import json

import django
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
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


if __name__ == '__main__':
    django.setup()
    storage_media = settings.MEDIA_ROOT
    from onbridge import models

    w3 = Web3(Web3.HTTPProvider(UPSTREAM, request_kwargs={'timeout': 120}))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    chain_id = w3.eth.chain_id
    bridge_address = w3.toChecksumAddress(BRIDGE_ADDRESS)
    token_contract = init_token(w3, TOKEN_ADDRESS, TOKEN_ABI_FILENAME)

    indexing_counter = 0
    while True:
        indexing_counter += 1
        log.info('indexing counter: {}'.format(indexing_counter))
        log.info('pause...')
        time.sleep(1)

        status = models.Status.objects.get(chain_id=chain_id)
        first_block = status.indexed_block

        last_block = w3.eth.get_block('latest')['number']
        log.info('start indexing process from {} block to {}...'.format(first_block, last_block))

        for block_number in range(first_block, last_block, STEP):
            log.info('sleep...')
            time.sleep(1)
            log.info('indexing process from {} block to {}'.format(first_block, last_block))
            log.info('current indexing block: {}'.format(block_number))

            event_transfer = token_contract.events.Transfer.createFilter(
                fromBlock=block_number,
                toBlock=block_number + STEP
            )
            events = event_transfer.get_all_entries()

            for event in events:
                if event.args.to == bridge_address or event.args.to == '0x0000000000000000000000000000000000000000':
                    log.info('token id {} on bridge: {}'.format(event.args.tokenId, bridge_address))
                    continue
                try:
                    token = models.Token.objects.get(token_id=event.args.tokenId)
                except ObjectDoesNotExist:
                    token = models.Token(token_id=event.args.tokenId)
                token.owner = event.args.to
                token.image = '{}.jpeg'.format(token.token_id)
                token.chain_id = chain_id
                token.tx = event.transactionHash.hex()
                token.block_number = event.blockNumber
                token.save()
                log.info('token id {} save to db'.format(token.token_id))
            status.indexed_block = last_block+1 if block_number + STEP > last_block else block_number + STEP+1
            status.save()
            log.info('next block number: {}'.format(status.indexed_block))

        log.info('done.')

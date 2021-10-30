import os
import logging
import time
import json

import django
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from web3 import Web3


log = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

STEP = 100
START_BLOCK = 13067662

UPSTREAM = os.environ['UPSTREAM']
TOKEN_ADDRESS = os.environ['TOKEN_ADDRESS']
TOKEN_ABI_FILENAME = os.environ['TOKEN_ABI_FILENAME']


def init_token(w3, address, abi_file_name):
    with open(abi_file_name, 'r') as f:
        data = json.load(f)

    return w3.eth.contract(abi=data['abi'], address=address)


if __name__ == '__main__':
    django.setup()
    storage_media = settings.MEDIA_ROOT
    from onbridge import models

    w3 = Web3(Web3.HTTPProvider(UPSTREAM, request_kwargs={'timeout': 120}))
    chain_id = w3.eth.chain_id
    token_contract = init_token(w3, TOKEN_ADDRESS, TOKEN_ABI_FILENAME)

    indexing_counter = 0
    while True:
        indexing_counter += 1
        log.info('pause...')
        time.sleep(1)

        last_indexed_block_number = models.Token.objects.order_by('-block_number').first()
        if last_indexed_block_number and last_indexed_block_number.block_number > START_BLOCK:
            first_block = last_indexed_block_number.block_number
        else:
            first_block = START_BLOCK

        last_block = w3.eth.get_block('latest')['number']
        log.info('start indexing process from {} block to {}...'.format(first_block, last_block))

        for block_number in range(first_block, last_block, STEP):
            log.info('indexing counter: {}'.format(indexing_counter))
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
                try:
                    token = models.Token.objects.get(token_id=event.args.tokenId)
                except ObjectDoesNotExist:
                    token = models.Token(token_id=event.args.tokenId)
                token.owner = event.args.to
                token.image = '{}.jpg'.format(token.token_id)
                token.chain_id = chain_id
                token.tx = event.transactionHash.hex()
                token.block_number = event.blockNumber
                token.save()
                log.info('token id {} save to db'.format(token.token_id))
            log.info('next events.')
        log.info('done.')

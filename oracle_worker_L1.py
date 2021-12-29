import os
import logging
import time
import json

import django
from web3 import Web3
from web3.middleware import geth_poa_middleware


log = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

WEB3_PROVIDER = os.environ['WEB3_PROVIDER']
BRIDGE_ADDRESS = os.environ['BRIDGE_ADDRESS']
BRIDGE_ABI_FILENAME = os.environ['BRIDGE_ABI_FILENAME']

STEP = 100

if __name__ == '__main__':
    django.setup()
    from onbridge.models import Action, Status
    w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER, request_kwargs={'timeout': 120}))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    bridge_address = w3.toChecksumAddress(BRIDGE_ADDRESS)
    with open(BRIDGE_ABI_FILENAME, 'r') as f:
        data = json.load(f)
    bridge_contract = w3.eth.contract(abi=data['abi'], address=BRIDGE_ADDRESS)

    log.info('run Action indexer')
    log.info('chain_id: {}'.format(w3.eth.chain_id))
    while True:
        log.info('pause...')
        time.sleep(1)
        indexer_status = Status.objects.get(chain_id=w3.eth.chain_id)
        first_block = indexer_status.oracle_block
        last_block = w3.eth.get_block('latest')['number']
        if first_block >= last_block:
            log.info(
                f'The new block has not been mined yet. Already Indexing block: {indexer_status.oracle_block}. '
                f'Last block on the chain: {last_block}.'
            )
            continue
        else:
            log.info(f'Scanning form {first_block} to {last_block}.')
        last_block = first_block + STEP if last_block - first_block >= STEP else last_block

        event_deposit_initiated = bridge_contract.events.DepositInitiated.createFilter(
            fromBlock=first_block,
            toBlock=last_block
        )
        deposit_events = event_deposit_initiated.get_all_entries()
        log.info(f'Got deposit events: {len(deposit_events)}')
        for event in deposit_events:
            if Action.objects.filter(l1_tx=event.transactionHash.hex()).first():
                log.warning(
                    f'The deposit event tx: {event.transactionHash.hex()} is present in the database.'
                )
                continue
            action = Action(
                sender=event.args._from,
                receiver=event.args._from,
                token_id=event.args._amount,
                l1_tx=event.transactionHash.hex(),
                direction=Action.Direction.DEPOSIT
            )
            action.save()
            log.info(
                f'The deposit event tx: {event.transactionHash.hex()} saved. Status NEW.'
            )

        indexer_status.oracle_block = last_block + 1

import os
import logging
import time
import json

import django
from django.conf import settings
from web3 import Web3
from web3.middleware import geth_poa_middleware


log = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

L1_UPSTREAM = os.environ['L1_UPSTREAM']
L2_UPSTREAM = os.environ['L2_UPSTREAM']
L1_BRIDGE_ADDRESS = os.environ['L1_BRIDGE_ADDRESS']
L2_BRIDGE_ADDRESS = os.environ['L2_BRIDGE_ADDRESS']
L1_BRIDGE_ABI_FILENAME = os.environ['L1_BRIDGE_ABI_FILENAME']
L2_BRIDGE_ABI_FILENAME = os.environ['L2_BRIDGE_ABI_FILENAME']
PRIVATE_KEY = os.environ['PRIVATE_KEY']
GAS_PRICE = int(os.environ['GAS_PRICE'])

STEP = 1000


def init_bridge(w3, address, abi_file_name):
    with open(abi_file_name, 'r') as f:
        data = json.load(f)

    return w3.eth.contract(abi=data['abi'], address=address)


if __name__ == '__main__':
    django.setup()
    storage_media = settings.MEDIA_ROOT
    from onbridge import models

    w3_l1 = Web3(Web3.HTTPProvider(L1_UPSTREAM, request_kwargs={'timeout': 120}))
    w3_l1.middleware_onion.inject(geth_poa_middleware, layer=0)
    bridge_address_l1 = w3_l1.toChecksumAddress(L1_BRIDGE_ADDRESS)
    chain_id_l1 = w3_l1.eth.chain_id
    bridge_contract_l1 = init_bridge(w3_l1, L1_BRIDGE_ADDRESS, L1_BRIDGE_ABI_FILENAME)

    account = w3_l1.eth.account.privateKeyToAccount(PRIVATE_KEY)

    w3_l2 = Web3(Web3.HTTPProvider(L2_UPSTREAM, request_kwargs={'timeout': 120}))
    w3_l2.middleware_onion.inject(geth_poa_middleware, layer=0)
    bridge_address_l2 = w3_l2.toChecksumAddress(L2_BRIDGE_ADDRESS)
    chain_id_l2 = w3_l2.eth.chain_id
    bridge_contract_l2 = init_bridge(w3_l2, L2_BRIDGE_ADDRESS, L2_BRIDGE_ABI_FILENAME)

    while True:
        log.info('pause...')
        time.sleep(1)
        log.info('chain_id: {}'.format(w3_l1.eth.chain_id))

        status = models.Status.objects.get(chain_id=chain_id_l1)
        first_block = status.oracle_block
        last_block = w3_l1.eth.get_block('latest')['number']
        log.info('start indexing process from {} block to {}...'.format(first_block, last_block))

        for block_number in range(first_block, last_block, STEP):
            log.info('sleep...')
            time.sleep(1)
            log.info('oracle process from {} block to {}'.format(first_block, last_block))
            log.info('current block: {}'.format(block_number))

            event_deposit_initiated = bridge_contract_l1.events.DepositInitiated.createFilter(
                fromBlock=block_number,
                toBlock=block_number + STEP
            )

            events = event_deposit_initiated.get_all_entries()

            for event in events:
                action = models.Action(
                    sender=event.args._from,
                    receiver=event.args._from,
                    token_id=event.args._amount,
                    l1_tx=event.transactionHash.hex(),
                    direction=models.Action.Direction.DEPOSIT
                )
                action.save()

                nonce = w3_l2.eth.get_transaction_count(account.address)
                tx = bridge_contract_l2.functions.finalizeInboundTransfer(
                    action.receiver, action.l1_tx, action.token_id
                ).buildTransaction(
                    {
                        'from': account.address,
                        'nonce': nonce,
                        'gasPrice': GAS_PRICE
                    }
                )
                signed_tx = w3_l2.eth.account.sign_transaction(tx, PRIVATE_KEY)
                w3_l2.eth.send_raw_transaction(signed_tx.rawTransaction)
                log.info('Tx Sent: {}'.format(signed_tx.hash.hex()))
                w3_l2.eth.wait_for_transaction_receipt(signed_tx.hash.hex())
                log.info('Tx Mined: {}'.format(signed_tx.hash.hex()))

                action.l2_tx = signed_tx.hash.hex()
                action.status = models.Action.Status.DONE
                action.save()
            status.indexed_block = last_block if block_number + STEP > last_block else block_number + STEP
            status.save()
            log.info('next events.')
        log.info('done.')

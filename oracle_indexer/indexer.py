import os
import logging
import time

import django
import requests

log = logging.getLogger(__name__)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

L1 = 97
TIME_SLEEP = 15


class Indexer:

    def __init__(self, _api, _uri_tx, _action_model):

        self.api = _api
        self.uri_tx = _uri_tx
        self.action_bridge_model = _action_model

    def _get_url_tx(self, _transaction_hash):

        return f"{self.api}{self.uri_tx.format(_transaction_hash)}"

    def _handling_actions(self, _actions, tx):

        for action in _actions:
            url = self._get_url_tx(getattr(action, tx))
            log.info(f'    API request  ...{url[27:]}')
            data = requests.get(url).json()
            send_data = data['send']
            claim_data = data.get('claim')
            if claim_data is None:
                log.info(f'    Oracle did not process bridging. skip')
                continue
            if L1 == send_data['eventOriginChainId']:
                action.l2_tx = claim_data['transactionHash']
                action.l2_chain_id = claim_data['eventOriginChainId']
            else:
                action.l1_tx = claim_data['transactionHash']
                action.l2_chain_id = send_data['eventOriginChainId']

            action.status = self.action_bridge_model.Status.DONE
            action.bridge_receiver = claim_data['receiver']
            action.save()
            log.info(f'    action handled')

        log.info('  handling actions finished')

    def handle(self):
        log.info('  handling actions in L1')
        actions_l1 = self.action_bridge_model.objects.filter(
            status=self.action_bridge_model.Status.NEW, l1_tx__isnull=False
        ).all()

        if actions_l1:
            self._handling_actions(actions_l1, 'l1_tx')
        else:
            log.info('    actions on the network L1 processed')

        log.info('  handling actions in L2')
        actions_l2 = self.action_bridge_model.objects.filter(
            status=self.action_bridge_model.Status.NEW, l2_tx__isnull=False
        ).all()

        if actions_l2:
            self._handling_actions(actions_l2, 'l2_tx')
        else:
            log.info('    actions on the network L2 processed')


if __name__ == '__main__':
    ORACLE_API = os.environ['ORACLE_API']
    URI_TX = os.environ['URI_TX']

    django.setup()
    from onbridge.models import ActionBridge

    log.info('Start Oracle API indexer')
    indexer = Indexer(ORACLE_API, URI_TX, ActionBridge)
    while True:
        indexer.handle()
        log.info(f'sleep {TIME_SLEEP} sec')
        time.sleep(TIME_SLEEP)

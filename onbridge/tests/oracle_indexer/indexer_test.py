from unittest.mock import patch, Mock

import requests
from django.test import TestCase

from onbridge.models import Token, ActionBridge
from oracle_indexer.indexer import Indexer
from .mock_envs import *


class OracleIndexerTests(TestCase):

    token_id = 1
    owner = 'Ox01'
    chain_id = 1
    tx = '0x01'
    block_number = 1

    bridge_sender = '0x001'
    bridge_receiver = '0x002'
    l1_tx = '0x123'
    l2_tx = '0x321'

    L1 = 97
    L2 = 42

    transaction_hash = "0x111"
    uri = ORACLE_API + URI_TX.format(transaction_hash)

    mock_response_json_L1 = {
        'send': {
            'eventOriginChainId': L1
        },
        'claim': {
            'eventOriginChainId': L2,
            'transactionHash': l2_tx,
            'receiver': bridge_receiver
        }
    }

    mock_response_json_L2 = {
        'send': {
            'eventOriginChainId': L2
        },
        'claim': {
            'eventOriginChainId': L1,
            'transactionHash': l1_tx,
            'receiver': bridge_receiver
        }
    }

    mock_response_json_oracle_not_processed = {
        'send': {
            'eventOriginChainId': L1
        }
    }

    def json_L1(self):
        return self.mock_response_json_L1

    def json_L2(self):
        return self.mock_response_json_L2

    def json_oracle_not_processed(self):
        return self.mock_response_json_oracle_not_processed

    def setUp(self) -> None:

        self.token = Token.objects.create(
            id=1,
            token_id=self.token_id,
            owner=self.owner,
            chain_id=self.chain_id,
            tx=self.tx,
            block_number=self.block_number
        )

        self.action_L1 = ActionBridge.objects.create(
            pk=1,
            bridge_sender=self.bridge_sender,
            direction=ActionBridge.Direction.DEPOSIT,
            token=self.token,
            l1_tx=self.l1_tx,
            status=ActionBridge.Status.NEW
        )

        self.action_L2 = ActionBridge.objects.create(
            pk=2,
            bridge_sender=self.bridge_sender,
            direction=ActionBridge.Direction.WITHDRAW,
            token=self.token,
            l2_tx=self.l2_tx,
            status=ActionBridge.Status.NEW
        )

        self.indexer = Indexer(ORACLE_API, URI_TX, ActionBridge)

    def test_init(self):
        self.assertEqual(self.indexer.api, ORACLE_API)
        self.assertEqual(self.indexer.uri_tx, URI_TX)
        self.assertEqual(self.indexer.action_bridge_model, ActionBridge)

    def test_get_url_tx(self):
        tx = self.indexer._get_url_tx(self.transaction_hash)

        self.assertEqual(self.uri, tx)

    @patch.object(requests, 'get')
    def test_handling_actions_on_bridge_L1(self, mock_get):
        mock_response = Mock(json=self.json_L1)
        mock_get.return_value = mock_response

        self.indexer._handling_actions([self.action_L1], 'l1_tx')

        action_l1 = ActionBridge.objects.get(pk=1)
        self.assertEqual(action_l1.l2_tx, self.l2_tx)
        self.assertEqual(action_l1.l2_chain_id, self.L2)
        self.assertEqual(action_l1.status, ActionBridge.Status.DONE)
        self.assertEqual(action_l1.bridge_receiver, self.bridge_receiver)

    @patch.object(requests, 'get')
    def test_handling_actions_on_bridge_L2(self, mock_get):
        mock_response = Mock(json=self.json_L2)
        mock_get.return_value = mock_response

        self.indexer._handling_actions([self.action_L2], 'l2_tx')

        action_l2 = ActionBridge.objects.get(pk=2)
        self.assertEqual(action_l2.l1_tx, self.l1_tx)
        self.assertEqual(action_l2.l2_chain_id, self.L2)
        self.assertEqual(action_l2.status, ActionBridge.Status.DONE)
        self.assertEqual(action_l2.bridge_receiver, self.bridge_receiver)

    @patch.object(requests, 'get')
    def test_handling_actions_oracle_not_processed(self, mock_get):
        mock_response = Mock(json=self.json_oracle_not_processed)
        mock_get.return_value = mock_response

        self.indexer._handling_actions([self.action_L1], 'l1_tx')

        action_l1 = ActionBridge.objects.get(pk=1)
        self.assertEqual(action_l1.l1_tx, self.l1_tx)
        self.assertEqual(action_l1.l2_chain_id, None)
        self.assertEqual(action_l1.status, ActionBridge.Status.NEW)
        self.assertEqual(action_l1.bridge_receiver, None)

    @patch.object(requests, 'get')
    def test_handle_L1(self, mock_get):
        mock_response = Mock(json=self.json_L1)
        mock_get.return_value = mock_response

        self.indexer.handle()

        action_l1 = ActionBridge.objects.get(pk=1)

        self.assertEqual(action_l1.l2_tx, self.l2_tx)
        self.assertEqual(action_l1.l2_chain_id, self.L2)
        self.assertEqual(action_l1.status, ActionBridge.Status.DONE)
        self.assertEqual(action_l1.bridge_receiver, self.bridge_receiver)

    @patch.object(requests, 'get')
    def test_handle_L2(self, mock_get):
        mock_response = Mock(json=self.json_L2)
        mock_get.return_value = mock_response

        self.indexer.handle()

        action_l2 = ActionBridge.objects.get(pk=2)

        self.assertEqual(action_l2.l1_tx, self.l1_tx)
        self.assertEqual(action_l2.l2_chain_id, self.L2)
        self.assertEqual(action_l2.status, ActionBridge.Status.DONE)
        self.assertEqual(action_l2.bridge_receiver, self.bridge_receiver)

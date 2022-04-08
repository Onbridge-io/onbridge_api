from unittest.mock import patch, Mock

from django.test import TestCase

from onbridge.models import Token, ActionBridge
from token_indexer.Indexer import Indexer
from .mock_envs import *


class HandleBridgeEventsTests(TestCase):

    token_id = 1
    owner = 'Ox01'
    chain_id = 1
    tx = '0x11'
    block_number = 123
    tx_action_deposit = '0x22'
    tx_action_withdraw = '0x33'
    bridge_sender = '0x12'

    class Entry:

        def __init__(self, _events):
            self.events = _events

        def get_all_entries(self):
            return self.events

    def hex_deposit(self):
        return self.tx_action_deposit

    def hex_withdraw(self):
        return self.tx_action_withdraw

    def createFilterDeposit(self, fromBlock, toBlock):
        return HandleBridgeEventsTests.Entry(self.mock_deposit_events)

    def createFilterWithdraw(self, fromBlock, toBlock):
        return HandleBridgeEventsTests.Entry(self.mock_withdraw_events)

    def patch_bridge_contract_events(self, obj, attr, _filter):
        setattr(obj, attr, Mock())
        setattr(getattr(obj, attr), 'createFilter', _filter)


    @patch('web3.Web3')
    def setUp(self, mock_web3) -> None:
        Token.objects.create(
            id=1,
            token_id=self.token_id,
            owner=self.owner,
            chain_id=self.chain_id,
            tx=self.tx,
            block_number=self.block_number
        )

        self.mock_deposit_events = [
            Mock(
                args=Mock(
                    _id=1
                ),
                address=self.bridge_sender,
                transactionHash=Mock(hex=self.hex_deposit)
            ),

        ]

        self.mock_withdraw_events = [
            Mock(
                args=Mock(
                    _id=1
                ),
                address=self.bridge_sender,
                transactionHash=Mock(hex=self.hex_withdraw)
            ),

        ]

        self.indexer = Indexer(
            w3=mock_web3(upstream='http://mock_upstream'),
            token_abi_filename=TOKEN_ABI_FILENAME,
            token_address=TOKEN_ADDRESS,
            bridge_address=BRIDGE_ADDRESS,
            bridge_abi_filename=BRIDGE_ABI_FILENAME,
            indexer_interval=INDEXER_INTERVAL,
            ipfs_host='http://mock_ipfs_host'
        )

        self.indexer.bridge_contract.events = Mock()
        self.patch_bridge_contract_events(
            self.indexer.bridge_contract.events, 'DepositInitiated', self.createFilterDeposit
        )
        self.patch_bridge_contract_events(
            self.indexer.bridge_contract.events, 'WithdrawalInitiated', self.createFilterWithdraw
        )

        self.indexer.action_model = ActionBridge
        self.indexer.token_model = Token

    def test_handel_deposit_events(self):
        self.indexer.handle_bridge_events(
            self.indexer.action_model.Direction.DEPOSIT, 'DepositInitiated', 1, 100
        )

        action = ActionBridge.objects.get(
            direction=ActionBridge.Direction.DEPOSIT,
            l1_tx=self.tx_action_deposit
        )

        self.assertEqual(action.token.token_id, self.token_id)
        self.assertEqual(action.direction, ActionBridge.Direction.DEPOSIT)
        self.assertEqual(action.status, ActionBridge.Status.NEW)
        self.assertEqual(action.bridge_sender, self.bridge_sender)
        self.assertEqual(action.bridge_receiver, None)
        self.assertEqual(action.l1_tx, self.tx_action_deposit)
        self.assertEqual(action.l2_tx, None)
        self.assertEqual(action.l2_chain_id, None)
        self.assertEqual(bool(action.created_at), True)
        self.assertEqual(bool(action.updated_at), True)

    def test_handel_withdraw_events(self):
        self.indexer.handle_bridge_events(
            self.indexer.action_model.Direction.WITHDRAW, 'WithdrawalInitiated', 1, 100
        )

        action = ActionBridge.objects.get(
            direction=ActionBridge.Direction.WITHDRAW,
            l2_tx=self.tx_action_withdraw
        )

        self.assertEqual(action.token.token_id, self.token_id)
        self.assertEqual(action.direction, ActionBridge.Direction.WITHDRAW)
        self.assertEqual(action.status, ActionBridge.Status.NEW)
        self.assertEqual(action.bridge_sender, self.bridge_sender)
        self.assertEqual(action.bridge_receiver, None)
        self.assertEqual(action.l1_tx, None)
        self.assertEqual(action.l2_tx, self.tx_action_withdraw)
        self.assertEqual(action.l2_chain_id, None)
        self.assertEqual(bool(action.created_at), True)
        self.assertEqual(bool(action.updated_at), True)

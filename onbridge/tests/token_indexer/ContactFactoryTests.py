import web3.exceptions
from web3 import Web3
from django.test import TestCase

from token_indexer.Indexer import Indexer
from .mock_envs import *


class ContactFactoryTests(TestCase):

    def setUp(self) -> None:
        self.indexer = Indexer(
            w3=Web3(Web3.HTTPProvider(UPSTREAM, request_kwargs={'timeout': 120})),
            token_abi_filename=TOKEN_ABI_FILENAME,
            token_address=TOKEN_ADDRESS,
            bridge_address=BRIDGE_ADDRESS,
            indexer_interval=INDEXER_INTERVAL,
            ipfs_host=IPFS_HOST,
            bridge_abi_filename=BRIDGE_ABI_FILENAME
        )

    def test_contract_taken_successfully(self):
        contact_token = self.indexer.get_contract_by_address_and_abi(
            self.indexer.token_address,
            TOKEN_ABI_FILENAME)
        self.assertEqual(contact_token.address, TOKEN_ADDRESS)

        contact_bridge = self.indexer.get_contract_by_address_and_abi(
            self.indexer.bridge_address,
            BRIDGE_ABI_FILENAME)
        self.assertEqual(contact_bridge.address, BRIDGE_ADDRESS)

    def test_contract_fails_with_wrong_address(self):
        self.assertRaises(web3.exceptions.InvalidAddress,
                          lambda:
                          self.indexer.get_contract_by_address_and_abi(
                              '0xdeadbeef',
                              TOKEN_ABI_FILENAME),
                          )

    def test_contract_fails_with_wrong_filename(self):
        self.assertRaises(
            FileNotFoundError,
            lambda:
            self.indexer.get_contract_by_address_and_abi(
                TOKEN_ADDRESS,
                'dummy.json'),
        )

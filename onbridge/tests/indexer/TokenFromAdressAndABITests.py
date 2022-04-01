import web3.exceptions
from django.test import TestCase

from token_indexer.Indexer import Indexer
from .mock_envs import *


class TokenFromAddressAndABITests(TestCase):

    def setUp(self) -> None:
        self.indexer = Indexer(
            upstream=UPSTREAM,
            token_abi_filename=TOKEN_ABI_FILENAME,
            token_address=TOKEN_ADDRESS,
            bridge_address=BRIDGE_ADDRESS,
            indexer_interval=INDEXER_INTERVAL,
            ipfs_host=IPFS_HOST
        )

    def test_contract_taken_successfully(self):
        token = self.indexer.get_token_by_address_and_abi(
            self.indexer.token_address,
            TOKEN_ABI_FILENAME)
        self.assertEqual(token.address, TOKEN_ADDRESS)

    def test_contract_fails_with_wrong_address(self):
        self.assertRaises(web3.exceptions.InvalidAddress,
                          lambda:
                          self.indexer.get_token_by_address_and_abi(
                              '0xdeadbeef',
                              TOKEN_ABI_FILENAME),
                          )

    def test_contract_fails_with_wrong_filename(self):
        self.assertRaises(
            FileNotFoundError,
            lambda:
            self.indexer.get_token_by_address_and_abi(
                TOKEN_ADDRESS,
                'dummy.json'),
        )

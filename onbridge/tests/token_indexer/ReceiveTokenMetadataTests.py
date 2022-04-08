from django.test import TestCase
from web3 import Web3

from .mock_envs import *
from token_indexer.Indexer import Indexer, IndexerException


class ReceiveTokenMetadataTests(TestCase):

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

    def test_successfully_received_metadata(self):
        metadata = self.indexer.get_token_metadata_from_contract(0)
        self.assertEqual(metadata, {'name': 'Pirate', 'description': 'Pirate that shines',
                                    'image': 'https://ipfs.io/ipfs/QmcsXTvsFrZXBLUsUuSWyP8x18xwhCgnmD8KwsijtuXk1e/0.png',
                                    'attributes': [{'trait_type': 'name', 'value': 'just noname pirate'}]}
                         )

    def test_fault_on_bad_token_id(self):
        self.assertRaises(
            IndexerException,
            lambda:
            self.indexer.get_token_metadata_from_contract(2 ** 257)
        )

    def test_fault_on_negative_token_id(self):
        self.assertRaises(
            IndexerException,
            lambda:
            self.indexer.get_token_metadata_from_contract(-1)
        )

    def test_mock_tokenURI_method(self):
        """
        Mocking indexer's contract. We replace function tokenURI to see behaviour of IPFS provider
        """
        mocked_indexer = Indexer(
            w3=Web3(Web3.HTTPProvider(UPSTREAM, request_kwargs={'timeout': 120})),
            token_abi_filename=TOKEN_ABI_FILENAME,
            token_address=TOKEN_ADDRESS,
            bridge_address=BRIDGE_ADDRESS,
            indexer_interval=INDEXER_INTERVAL,
            ipfs_host=IPFS_HOST,
            bridge_abi_filename=BRIDGE_ABI_FILENAME
        )
        # Now contract will tell us wrong tokenURI
        mocked_indexer.token_contract.functions.tokenURI = lambda token_id: f"google.com/{token_id}"
        self.assertRaises(
            IndexerException,
            lambda: mocked_indexer.get_token_metadata_from_contract(0)
        )

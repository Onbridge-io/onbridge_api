import os

from django.test import TestCase

from onbridge.models import Token
from token_indexer.Indexer import Indexer
from .mock_envs import *
from pathlib import Path


class MockTransactionHash:

    def __init__(self, hex_value: str):
        self.hex_value = hex_value

    def hex(self):
        return self.hex_value


class MockEventArgs:
    tokenId: int
    to: str

    def __init__(self, token_id: int, to: str):
        self.tokenId = token_id
        self.to = to


class MockEvent:
    args: MockEventArgs
    blockNumber: int
    transactionHash: MockTransactionHash

    def __init__(self, tokenId: int, to: str, blockNumber: int, tx_hash: MockTransactionHash):
        self.args = MockEventArgs(tokenId, to)
        self.blockNumber = blockNumber
        self.transactionHash = tx_hash


class IndexNewTokenTests(TestCase):

    def setUp(self) -> None:
        self.indexer = Indexer(
            upstream=UPSTREAM,
            token_abi_filename=TOKEN_ABI_FILENAME,
            token_address=TOKEN_ADDRESS,
            bridge_address=BRIDGE_ADDRESS,
            indexer_interval=INDEXER_INTERVAL,
            ipfs_host=IPFS_HOST,
            bridge_abi_filename=BRIDGE_ABI_FILENAME
        )
        self.token_id = 0
        # mocking media storage to prevent test data corrupting main media volume
        self.indexer.storage_media = MOCK_STORAGE_MEDIA_ROOT

        # dir for media of token
        self.media_path_with_ipfs = Path(self.indexer.storage_media, MOCK_IPFS_ADDRESS)

        token_file = Path(self.media_path_with_ipfs, f"{self.token_id}.png")
        # clear token file before run tests
        if token_file.exists():
            os.remove(token_file)

        # create dir to make sure files will be written
        Path.mkdir(Path(self.media_path_with_ipfs), exist_ok=True, parents=True)

    def test_successfully_indexed_token(self):
        mock_event = MockEvent(self.token_id, '0xdeadbeef', 16780309, MockTransactionHash('0xdummyhash'))
        self.indexer.index_new_token(mock_event)
        created_token = Token.objects.first()
        self.assertEqual(1644941452, created_token.blockchain_timestamp)
        self.assertEqual('0xdummyhash', created_token.tx)
        self.assertEqual(self.token_id, created_token.token_id)
        self.assertEqual('0xdeadbeef', created_token.owner)

    def test_successfully_move_token_between_chains(self):
        block_number_before_move = 16780309
        mock_event_before_move = MockEvent(
            self.token_id, '0xdeadbeef', block_number_before_move, MockTransactionHash('0xdummyhash_old')
        )

        # mock IPFS fetching image function. Now it just creates empty PNG file
        # with token_id as filename
        self.indexer.fetch_image = lambda token: Path(
            self.media_path_with_ipfs, f"{token.token_id}.png"
        ).open("w").close()
        self.indexer.index_new_token(mock_event_before_move)
        token_before_move: Token = Token.objects.first()
        self.assertEqual(97, token_before_move.chain_id)

        # mock changing chain. Anyway we don't need to change anything else
        chain_id_after_move = 80001
        self.indexer.chain_id = chain_id_after_move

        # we also mock that some period of time has passed
        block_number_after_move = block_number_before_move + 100

        # to mock that new event (after move) is later than the previous one
        mock_event_after_move = MockEvent(
            self.token_id, '0xdeadbeef', block_number_after_move, MockTransactionHash('0xdummyhash_new')
        )

        self.indexer.index_new_token(mock_event_after_move)

        # make sure that indexer did not duplicate tokens in database
        self.assertEqual(1, Token.objects.count())

        token_after_move: Token = Token.objects.first()
        # make sure indexer changed chain id to new chainId
        self.assertEqual(chain_id_after_move, token_after_move.chain_id)

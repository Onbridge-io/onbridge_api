import os

from Indexer import Indexer

UPSTREAM = os.environ['UPSTREAM']
TOKEN_ADDRESS = os.environ['TOKEN_ADDRESS']
TOKEN_ABI_FILENAME = os.environ['TOKEN_ABI_FILENAME']
BRIDGE_ADDRESS = os.environ['BRIDGE_ADDRESS']
INDEXER_INTERVAL = int(os.environ['INDEXER_INTERVAL'])
IPFS_HOST = os.environ["IPFS_HOST"]

if __name__ == "__main__":
    Indexer(
        upstream=UPSTREAM,
        ipfs_host=IPFS_HOST,
        bridge_address=BRIDGE_ADDRESS,
        indexer_interval=INDEXER_INTERVAL,
        token_address=TOKEN_ADDRESS,
        token_abi_filename=TOKEN_ABI_FILENAME
    ).main_cycle()

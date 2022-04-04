import os
import sys

UPSTREAM = os.environ['UPSTREAM']
TOKEN_ADDRESS = os.environ['TOKEN_ADDRESS']
TOKEN_ABI_FILENAME = os.environ['TOKEN_ABI_FILENAME']
BRIDGE_ADDRESS = os.environ['BRIDGE_ADDRESS']
BRIDGE_ABI_FILENAME = os.environ['BRIDGE_ABI_FILENAME']
INDEXER_INTERVAL = int(os.environ['INDEXER_INTERVAL'])
IPFS_HOST = os.environ["IPFS_HOST"]


def main():
    """
    Token indexer start:
    1) Setup django dir to take all necessary packages (i.e. settings)
    2) Start indexer with envs

    Example of how to execute is described in README.md
    """
    django_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(django_dir)
    sys.path.append(django_dir)
    from Indexer import Indexer
    Indexer(
        upstream=UPSTREAM,
        ipfs_host=IPFS_HOST,
        bridge_address=BRIDGE_ADDRESS,
        indexer_interval=INDEXER_INTERVAL,
        token_address=TOKEN_ADDRESS,
        token_abi_filename=TOKEN_ABI_FILENAME,
        bridge_abi_filename=BRIDGE_ABI_FILENAME
    ).main_cycle()


if __name__ == "__main__":
    main()

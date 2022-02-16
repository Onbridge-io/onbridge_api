import logging
import os

import django

log = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')


def main():
    # bsc config
    Status.objects.get_or_create(
        chain_id=os.environ['BSC_CHAIN_ID'],
        defaults={
            'indexed_block': os.environ['BSC_START_BLOCK']
        })


    # eth config
    Status.objects.get_or_create(
        chain_id=os.environ['ETH_CHAIN_ID'],
        defaults={
            'indexed_block': os.environ['ETH_START_BLOCK']
        })

    # polygon config
    Status.objects.get_or_create(
        chain_id=os.environ['POLYGON_CHAIN_ID'],
        defaults={
            'indexed_block': os.environ['POLYGON_START_BLOCK']
        })

    log.info('successfully created')


if __name__ == '__main__':
    django.setup()
    from onbridge.models import Status
    main()

import os
import logging

import django
from django.core.exceptions import ObjectDoesNotExist


log = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')


def main():

    try:
        chain_id_1 = models.Status.objects.get(chain_id=os.environ['L1_CHAIN_ID'])
    except ObjectDoesNotExist:
        chain_id_1 = models.Status(chain_id=os.environ['L1_CHAIN_ID'])
    chain_id_1.indexed_block = os.environ['L1_START_BLOCK']
    chain_id_1.oracle_block = os.environ['L1_START_BLOCK']
    chain_id_1.save()

    try:
        chain_id_2 = models.Status.objects.get(chain_id=os.environ['L2_CHAIN_ID'])
    except ObjectDoesNotExist:
        chain_id_2 = models.Status(chain_id=os.environ['L2_CHAIN_ID'])
    chain_id_2.indexed_block = os.environ['L2_START_BLOCK']
    chain_id_2.oracle_block = os.environ['L2_START_BLOCK']
    chain_id_2.save()

    log.info('successfully created')


if __name__ == '__main__':
    django.setup()
    from onbridge import models
    main()

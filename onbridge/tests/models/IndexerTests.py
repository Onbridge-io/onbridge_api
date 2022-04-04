from django.test import TestCase
from onbridge import models


class IndexerTests(TestCase):
    chain_id = 1
    indexed_block = 123

    def setUp(self):
        indexer = models.Indexer(
            id=1,
            chain_id=self.chain_id,
            indexed_block=self.indexed_block
        )
        indexer.save()

    def test_model(self):
        indexer = models.Indexer.objects.get(id=1)
        self.assertEqual(indexer.chain_id, self.chain_id)
        self.assertEqual(indexer.indexed_block, self.indexed_block)
        self.assertEqual(models.Indexer.objects.count(), 1)

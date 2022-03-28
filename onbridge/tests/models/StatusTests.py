from django.test import TestCase
from onbridge import models


class StatusTests(TestCase):
    chain_id = 1
    indexed_block = 123

    def setUp(self):
        status = models.Status(
            id=1,
            chain_id=self.chain_id,
            indexed_block=self.indexed_block
        )
        status.save()

    def test_model(self):
        status = models.Status.objects.get(id=1)
        self.assertEqual(status.chain_id, self.chain_id)
        self.assertEqual(status.indexed_block, self.indexed_block)
        self.assertEqual(models.Status.objects.count(), 1)

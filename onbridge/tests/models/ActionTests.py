import django
from django.test import TestCase


from onbridge import models


class ActionTests(TestCase):

    token_id = 1
    owner = 'Ox01'
    chain_id = 1
    tx = '0x01'
    block_number = 1
    skill = 0

    bridge_sender = '0x001'
    bridge_receiver = '0x002'
    l1_tx = '0x123'
    l2_tx = '1x123'
    l2_chain_id = 1

    def setUp(self):

        self.token = models.Token.objects.create(
            id=1,
            token_id=self.token_id,
            owner=self.owner,
            chain_id=self.chain_id,
            tx=self.tx,
            block_number=self.block_number
        )

        models.Action.objects.create(
            pk=2,
            bridge_sender=self.bridge_sender,
            bridge_receiver=self.bridge_receiver,
            direction=models.Action.Direction.DEPOSIT,
            token=self.token,
            l1_tx=self.l1_tx,
            l2_tx=self.l2_tx,
            l2_chain_id=self.l2_chain_id,
            status=models.Action.Status.NEW
        )

    def test_model(self):
        action = models.Action.objects.get(pk=2)
        self.assertEqual(action.bridge_sender, self.bridge_sender)
        self.assertEqual(action.bridge_receiver, self.bridge_receiver)
        self.assertEqual(action.direction, models.Action.Direction.DEPOSIT)
        self.assertEqual(action.token_id, self.token_id)
        self.assertEqual(action.l1_tx, self.l1_tx)
        self.assertEqual(action.l2_tx, self.l2_tx)
        self.assertEqual(action.status, models.Action.Status.NEW)
        self.assertEqual(bool(action.created_at), True)

    def test_model_data_types_bridge_sender(self):

        with self.assertRaises(django.db.utils.IntegrityError):
            models.Action.objects.create(
                bridge_receiver=self.bridge_receiver,
                direction=models.Action.Direction.DEPOSIT,
                token=self.token,
                l1_tx=self.l1_tx,
                l2_tx=self.l2_tx,
                l2_chain_id=self.l2_chain_id,
                status=models.Action.Status.NEW
            )

    def test_model_data_types_bridge_receiver(self):

        with self.assertRaises(django.db.utils.IntegrityError):
            models.Action.objects.create(
                bridge_sender=self.bridge_sender,
                direction=models.Action.Direction.DEPOSIT,
                token=self.token,
                l1_tx=self.l1_tx,
                l2_tx=self.l2_tx,
                l2_chain_id=self.l2_chain_id,
                status=models.Action.Status.NEW
            )

    def test_model_data_types_direction(self):
        with self.assertRaises(django.db.utils.IntegrityError):
            models.Action.objects.create(
                bridge_sender=self.bridge_sender,
                bridge_receiver=self.bridge_receiver,
                direction=3,
                token=self.token,
                l1_tx=self.l1_tx,
                l2_tx=self.l2_tx,
                l2_chain_id=self.l2_chain_id,
                status=models.Action.Status.NEW
            )

    def test_model_data_types_token_id(self):
        with self.assertRaises(django.db.utils.IntegrityError):
            models.Action.objects.create(
                bridge_sender=self.bridge_sender,
                bridge_receiver=self.bridge_receiver,
                direction=models.Action.Direction.DEPOSIT,
                l1_tx=self.l1_tx,
                l2_tx=self.l2_tx,
                l2_chain_id=self.l2_chain_id,
                status=models.Action.Status.NEW
            )

    def test_model_data_types_tx_1(self):
        with self.assertRaises(django.db.utils.IntegrityError):
            models.Action.objects.create(
                bridge_sender=self.bridge_sender,
                bridge_receiver=self.bridge_receiver,
                direction=models.Action.Direction.DEPOSIT,
                token=self.token,
                l2_tx=self.l2_tx,
                l2_chain_id=self.l2_chain_id,
                status=models.Action.Status.NEW
            )

    def test_model_data_types_tx_2(self):
        with self.assertRaises(django.db.utils.IntegrityError):
            models.Action.objects.create(
                bridge_sender=self.bridge_sender,
                bridge_receiver=self.bridge_receiver,
                direction=models.Action.Direction.DEPOSIT,
                token=self.token,
                l2_tx=self.l2_tx,
                l2_chain_id=self.l2_chain_id,
                status=models.Action.Status.NEW
            )

    def test_model_data_types_l2_chain_id(self):
        with self.assertRaises(django.db.utils.IntegrityError):
            models.Action.objects.create(
                bridge_receiver=self.bridge_receiver,
                direction=models.Action.Direction.DEPOSIT,
                token=self.token,
                l1_tx=self.l1_tx,
                l2_tx=self.l2_tx,
                status=models.Action.Status.NEW
            )

    def test_model_data_types_status(self):
        with self.assertRaises(django.db.utils.IntegrityError):
            models.Action.objects.create(
                bridge_sender=self.bridge_sender,
                bridge_receiver=self.bridge_receiver,
                direction=models.Action.Direction.DEPOSIT,
                token=self.token,
                l1_tx=self.l1_tx,
                l2_tx=self.l2_tx,
                l2_chain_id=self.l2_chain_id,
                status=3
            )

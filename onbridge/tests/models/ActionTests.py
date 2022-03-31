import django
from django.test import TestCase


from onbridge import models


class ActionTests(TestCase):

    sender = '0x001'
    receiver = '0x002'
    token_id = 0
    l1_tx = '0x123'
    l2_tx = '1x123'

    def setUp(self):
        models.Action.objects.create(
            pk=2,
            sender=self.sender,
            receiver=self.receiver,
            direction=models.Action.Direction.DEPOSIT,
            token_id=self.token_id,
            l1_tx=self.l1_tx,
            l2_tx=self.l2_tx,
            status=models.Action.Status.NEW
        )

    def test_model(self):
        action = models.Action.objects.get(pk=2)
        self.assertEqual(action.sender, self.sender)
        self.assertEqual(action.receiver, self.receiver)
        self.assertEqual(action.direction, models.Action.Direction.DEPOSIT)
        self.assertEqual(action.token_id, self.token_id)
        self.assertEqual(action.l1_tx, self.l1_tx)
        self.assertEqual(action.l2_tx, self.l2_tx)
        self.assertEqual(action.status, models.Action.Status.NEW)
        self.assertEqual(bool(action.created_at), True)

    def test_model_data_types_sender(self):

        with self.assertRaises(django.db.utils.IntegrityError):
            models.Action.objects.create(
                receiver=self.receiver,
                direction=models.Action.Direction.DEPOSIT,
                token_id=self.token_id,
                l1_tx=self.l1_tx,
                l2_tx=self.l2_tx,
                status=models.Action.Status.NEW
            )

    def test_model_data_types_receiver(self):

        with self.assertRaises(django.db.utils.IntegrityError):
            models.Action.objects.create(
                sender=self.sender,
                direction=models.Action.Direction.DEPOSIT,
                token_id=self.token_id,
                l1_tx=self.l1_tx,
                l2_tx=self.l2_tx,
                status=models.Action.Status.NEW
            )

    def test_model_data_types_direction(self):
        with self.assertRaises(django.db.utils.IntegrityError):
            models.Action.objects.create(
                sender=self.sender,
                receiver=self.receiver,
                direction=3,
                token_id=self.token_id,
                l1_tx=self.l1_tx,
                l2_tx=self.l2_tx,
                status=models.Action.Status.NEW
            )

    def test_model_data_types_token_id(self):
        with self.assertRaises(django.db.utils.IntegrityError):
            models.Action.objects.create(
                sender=self.sender,
                receiver=self.receiver,
                direction=models.Action.Direction.DEPOSIT,
                l1_tx=self.l1_tx,
                l2_tx=self.l2_tx,
                status=models.Action.Status.NEW
            )

    def test_model_data_types_tx_1(self):
        with self.assertRaises(django.db.utils.IntegrityError):
            models.Action.objects.create(
                sender=self.sender,
                receiver=self.receiver,
                direction=models.Action.Direction.DEPOSIT,
                token_id=self.token_id,
                l2_tx=self.l2_tx,
                status=models.Action.Status.NEW
            )

    def test_model_data_types_tx_2(self):
        with self.assertRaises(django.db.utils.IntegrityError):
            models.Action.objects.create(
                sender=self.sender,
                receiver=self.receiver,
                direction=models.Action.Direction.DEPOSIT,
                token_id=self.token_id,
                l2_tx=self.l2_tx,
                status=models.Action.Status.NEW
            )

    def test_model_data_types_status(self):
        with self.assertRaises(django.db.utils.IntegrityError):
            models.Action.objects.create(
                sender=self.sender,
                receiver=self.receiver,
                direction=models.Action.Direction.DEPOSIT,
                token_id=self.token_id,
                l1_tx=self.l1_tx,
                l2_tx=self.l2_tx,
                status=3
            )

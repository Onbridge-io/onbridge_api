from django.db import models


class Status(models.Model):
    chain_id = models.PositiveIntegerField(unique=True)
    indexed_block = models.PositiveBigIntegerField()
    oracle_block = models.PositiveBigIntegerField()


class Token(models.Model):
    token_id = models.PositiveIntegerField(unique=True)
    owner = models.CharField(max_length=255, verbose_name='Owners')
    image = models.FileField(upload_to='images/')
    chain_id = models.PositiveIntegerField()
    tx = models.CharField(max_length=255, verbose_name='Tx hashes')
    block_number = models.PositiveBigIntegerField()
    skill = models.IntegerField(default=0)
    date_updated = models.DateTimeField(auto_now=True)


class Action(models.Model):

    class Direction(models.IntegerChoices):
        DEPOSIT = 1
        WITHDRAW = 2

    class Status(models.IntegerChoices):
        NEW = 1
        DONE = 2

    sender = models.CharField(max_length=255, verbose_name='Senders')
    receiver = models.CharField(max_length=255, verbose_name='Receivers')
    direction = models.IntegerField(choices=Direction.choices)
    token_id = models.PositiveIntegerField()
    l1_tx = models.CharField(max_length=255, verbose_name='L1 tx hashes')
    l2_tx = models.CharField(max_length=255, verbose_name='L2 tx hashes')
    status = models.IntegerField(choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

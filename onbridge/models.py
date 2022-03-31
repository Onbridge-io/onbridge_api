from django.db import models


class Status(models.Model):
    chain_id = models.PositiveIntegerField(unique=True)
    indexed_block = models.PositiveBigIntegerField()

    class Meta:
        verbose_name_plural = "statuses"


class Token(models.Model):
    token_id = models.PositiveIntegerField(unique=True)
    owner = models.CharField(max_length=255, verbose_name='Owners')
    image = models.FileField(upload_to='images/')
    chain_id = models.PositiveIntegerField()
    tx = models.CharField(max_length=255)
    block_number = models.PositiveBigIntegerField()
    skill = models.IntegerField(default=0)
    date_updated = models.DateTimeField(auto_now=True)
    blockchain_timestamp = models.PositiveBigIntegerField(null=True, default=None)
    ipfs_uri_image = models.CharField(max_length=100, verbose_name='ifps uri image')

    def __str__(self):
        return f"<Token Object>: Owner {self.owner} has token with id={self.token_id} on chain with id={self.chain_id}."


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
    l1_tx = models.CharField(max_length=255)
    l2_tx = models.CharField(max_length=255)
    status = models.IntegerField(choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=~models.Q(sender=""), name="non_empty_sender"),
            models.CheckConstraint(check=~models.Q(receiver=""), name="non_empty_receiver"),
            models.CheckConstraint(check=~models.Q(l1_tx=""), name="non_empty_l1_tx"),
            models.CheckConstraint(check=~models.Q(l2_tx=""), name="non_empty_l2_tx"),
            models.CheckConstraint(check=models.Q(direction__in=[1, 2]), name="Direction_choices"),
            models.CheckConstraint(check=models.Q(status__in=[1, 2]), name="Status_choices")
        ]

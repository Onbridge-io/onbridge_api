from django.db import models


class Token(models.Model):
    token_id = models.PositiveIntegerField()
    owner = models.CharField(max_length=255, verbose_name='Owners')
    image = models.FileField(upload_to='images/')
    chain_id = models.PositiveIntegerField()
    tx = models.CharField(max_length=255, verbose_name='Tx hashes')
    block = models.PositiveBigIntegerField()

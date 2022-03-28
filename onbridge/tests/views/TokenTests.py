from rest_framework.test import APITestCase
from onbridge import models, serializers
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from django.urls import reverse


class TokenTests(APITestCase):
    token_id = 1
    owner = 'Ox01'
    chain_id = 1
    tx = '0x01'
    block_number = 1
    skill = 0

    def setUp(self):
        token = models.Token(
            id=1,
            token_id=self.token_id,
            owner=self.owner,
            chain_id=self.chain_id,
            tx=self.tx,
            block_number=self.block_number
        )
        token.save()

    def test_model(self):
        token = models.Token.objects.get(id=1)
        self.assertEqual(token.token_id, self.token_id)
        self.assertEqual(token.owner, self.owner)
        self.assertEqual(token.chain_id, self.chain_id)
        self.assertEqual(token.tx, self.tx)
        self.assertEqual(token.block_number, self.block_number)
        self.assertEqual(token.skill, self.skill)
        self.assertEqual(models.Token.objects.count(), 1)

    def test_view(self):
        url = reverse('token-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_view_get_item(self):
        response = self.client.get('/api/tokens/1/')
        token = models.Token.objects.get(id=1)
        serializer = serializers.TokenSerializer(token)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_view_get_does_not_exist_item(self):
        response = self.client.get('/api/tokens/123/')
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

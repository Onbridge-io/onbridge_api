from datetime import date

from django.test import Client, TestCase
from rest_framework.status import HTTP_400_BAD_REQUEST

from onbridge import models


class TokenChainIdFilterTests(TestCase):
    # information how many tokens (value) are dedicated to chain id (key)
    tokens_generation_info = {
        97: 100,
        42: 10,
        80001: 20,
    }

    def setUp(self) -> None:
        general_token_id_iter = 0
        for chain_id in self.tokens_generation_info:
            for i in range(self.tokens_generation_info[chain_id]):
                models.Token.objects.create(
                    token_id=general_token_id_iter,
                    chain_id=chain_id,
                    block_number=123,
                    date_updated=date.today(),
                    image='',
                    owner='0x000',
                    skill=0,
                )
                general_token_id_iter += 1

        self.client = Client()

    def test_successfully_filtered(self):
        for chain_id in self.tokens_generation_info:
            response = self.client.get(f"/api/tokens/?chain_id={chain_id}")
            response_in_json = response.json()
            expected_count = self.tokens_generation_info[chain_id]
            actual_count = response_in_json['count']
            self.assertEqual(actual_count, expected_count)
            results = response_in_json['results']
            for token in results:
                self.assertEqual(token['chainId'], chain_id)

    def test_filter_by_non_existent_chain_id(self):
        response = self.client.get(f"/api/tokens/?chain_id=228")
        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code)

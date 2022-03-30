from datetime import date

from django.test import Client, TestCase

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
            response = self.client.get(f"/api/tokens/?chainId={chain_id}")
            response_in_json = response.json()
            expected_count = self.tokens_generation_info[chain_id]
            actual_count = response_in_json['count']
            self.assertEqual(actual_count, expected_count)
            results = response_in_json['results']
            for token in results:
                self.assertEqual(token['chainId'], chain_id)

    def test_filter_by_non_existent_chain_id(self):
        response = self.client.get("/api/tokens/?chainId=228")
        self.assertEqual(200, response.status_code)

    def test_filter_with_comma_separated(self):
        chain_ids = map(str, self.tokens_generation_info.keys())
        response = self.client.get(f"/api/tokens/?chainId={','.join(chain_ids)}")
        data = response.json()
        self.assertEqual(data['count'], sum(self.tokens_generation_info.values()))

    def test_filter_with_bad_comma_separated(self):
        response = self.client.get("/api/tokens/?chainId=1,2,3,,,44")
        data = response.json()
        self.assertEqual(0, data['count'])

    def test_filter_with_letters_in_query(self):
        response = self.client.get("/api/tokens/?chainId=1,a,b,c,2,3,4")
        data = response.json()
        self.assertEqual(0, data['count'])

    def test_filter_with_strange_chars(self):
        response = self.client.get("/api/tokens/?chainId=^,&@,YB,FYB,&,#$H(")
        data = response.json()
        self.assertEqual(0, data['count'])

    def test_filter_with_empty_param(self):
        response_without_filter = self.client.get("/api/tokens/")
        response_with_filter = self.client.get("/api/tokens/?chainId=")
        data_without_filter = response_without_filter.json()
        data_with_filter = response_with_filter.json()
        self.assertEqual(data_with_filter['count'], data_without_filter['count'])
        self.assertEqual(data_with_filter['count'], sum(self.tokens_generation_info.values()))

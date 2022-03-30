from django.test import TestCase, Client
from onbridge import models


class TokenOwnerFilterTests(TestCase):
    owners = [
        '0xdeadbeef',
        '0x010101',
        '0xded',
        '0xfeed',
        '0xdad'
    ]

    amount = [x for x in range(10, 100, 10)]

    # how much generate tokens to specific owner
    generation_data = dict(zip(owners, amount))

    client = Client()

    def setUp(self) -> None:
        general_token_iter = 0
        for owner in self.generation_data:
            for i in range(self.generation_data[owner]):
                models.Token.objects.create(
                    owner=owner,
                    token_id=general_token_iter,
                    chain_id=42,
                    block_number=228,
                    skill=100,
                    image='google.com',
                    tx=0x00
                )
                general_token_iter += 1

    def test_filter_by_owner_successfully(self):
        for owner in self.owners:
            response = self.client.get(f'/api/tokens/?owner={owner}')
            actual_count = response.json()['count']
            expected_count = self.generation_data[owner]
            self.assertEqual(actual_count, expected_count)

    def test_filter_by_non_existing_owner(self):
        response = self.client.get("/api/tokens/?owner=dummy_owner")
        self.assertEqual(0, response.json()['count'])

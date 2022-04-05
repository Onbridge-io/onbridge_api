from rest_framework.test import APITestCase
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN


from onbridge import models, serializers


class ActionBridgeTestsView(APITestCase):

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

        self.action = models.ActionBridge.objects.create(
            pk=1,
            bridge_sender=self.bridge_sender,
            bridge_receiver=self.bridge_receiver,
            direction=models.ActionBridge.Direction.DEPOSIT,
            token=self.token,
            l1_tx=self.l1_tx,
            l2_tx=self.l2_tx,
            l2_chain_id=self.l2_chain_id,
            status=models.ActionBridge.Status.NEW
        )

    def test_view(self):
        response = self.client.get('/api/actions/')
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_view_get_item(self):
        response = self.client.get('/api/actions/1/')
        serializer = serializers.ActionBridgeSerializer(self.action)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_view_get_does_not_exist_item(self):
        response = self.client.get('/api/actions/123/')
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_view_unsupported_method_post(self):
        response = self.client.post('/api/actions/1/', data={'mock': 123})
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_view_unsupported_method_put(self):
        response = self.client.put('/api/actions/1/', data={'mock': 123})
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_view_unsupported_method_patch(self):
        response = self.client.post('/api/actions/1/', data={'mock': 123})
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_view_unsupported_method_delete(self):
        response = self.client.delete('/api/actions/1/')
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)


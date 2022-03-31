from rest_framework.test import APITestCase
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN


from onbridge import models, serializers


class ActionTestsView(APITestCase):

    sender = '0x001'
    receiver = '0x002'
    token_id = 0
    l1_tx = '0x123'
    l2_tx = '1x123'

    def setUp(self):
        self.action = models.Action.objects.create(
            pk=1,
            sender=self.sender,
            receiver=self.receiver,
            direction=models.Action.Direction.DEPOSIT,
            token_id=self.token_id,
            l1_tx=self.l1_tx,
            l2_tx=self.l2_tx,
            status=models.Action.Status.NEW
        )

    def test_view(self):
        response = self.client.get('/api/actions/')
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_view_get_item(self):
        response = self.client.get('/api/actions/1/')
        serializer = serializers.ActionSerializer(self.action)
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


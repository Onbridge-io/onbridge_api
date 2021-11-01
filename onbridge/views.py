from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from . import models
from . import serializers


class TokenView(viewsets.ModelViewSet):
    lookup_field = 'token_id'
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = serializers.TokenSerializer
    queryset = models.Token.objects.all().order_by('token_id')
    http_method_names = ['get', 'options', 'head']

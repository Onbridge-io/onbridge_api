from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

from . import models
from . import serializers


class TokenView(viewsets.ModelViewSet):
    http_method_names = ['get', 'options', 'head']
    lookup_field = 'token_id'
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = serializers.TokenSerializer
    queryset = models.Token.objects.all().order_by('token_id')
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['owner']

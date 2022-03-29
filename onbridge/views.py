from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters import FilterSet
from django_filters.filters import AllValuesMultipleFilter

from . import models
from . import serializers


class TokenFilter(FilterSet):
    chain_id = AllValuesMultipleFilter()

    class Meta:
        model = models.Token
        fields = ['chain_id']


class TokenView(viewsets.ModelViewSet):
    lookup_field = 'token_id'
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = serializers.TokenSerializer
    queryset = models.Token.objects.all().order_by('token_id')
    http_method_names = ['get', 'options', 'head']
    filterset_class = TokenFilter

import logging

from django.db.models import QuerySet
from django_filters import FilterSet
from django_filters.filters import CharFilter
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from . import models
from . import serializers


class ChainIdFilter(CharFilter):

    def filter(self, qs: QuerySet, value: str):
        if value:
            try:
                items = list(map(int, value.split(",")))
                return qs.filter(chain_id__in=items)
            except Exception as e:
                logging.info(f"When filtering tokens by chainId error was caught: {e}")
                return qs.none()
        else:
            return qs


class TokenFilterSet(FilterSet):
    chainId = ChainIdFilter(label='Chain ID', field_name='chain_id', lookup_expr='in')
    skill_ability = CharFilter(field_name='skill')

    class Meta:
        model = models.Token
        fields = ['owner']


class TokenView(viewsets.ModelViewSet):
    lookup_field = 'token_id'
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = serializers.TokenSerializer
    queryset = models.Token.objects.all().order_by('token_id')
    http_method_names = ['get', 'options', 'head']
    filterset_class = TokenFilterSet


class ActionBridgeView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = serializers.ActionBridgeSerializer
    queryset = models.ActionBridge.objects.all()
    http_method_names = ['get', 'options', 'head']

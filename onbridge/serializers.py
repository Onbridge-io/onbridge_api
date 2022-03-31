from rest_framework import serializers

from . import models


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Token
        fields = '__all__'


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Action
        fields = '__all__'

from rest_framework import serializers

from . import models


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Token
        fields = '__all__'


class ActionBridgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ActionBridge
        fields = '__all__'

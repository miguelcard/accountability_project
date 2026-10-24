from rest_framework import serializers
from Models.notifications.models import DeviceToken


class DeviceTokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=512)
    platform = serializers.ChoiceField(choices=[c[0] for c in DeviceToken.PLATFORM_CHOICES])


class DeviceTokenDeleteSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=512)

import logging
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Models.notifications.api.serializers import DeviceTokenSerializer, DeviceTokenDeleteSerializer
from Models.notifications.models import DeviceToken

logger = logging.getLogger(__name__)


class DeviceTokenApiView(APIView):
    """
    POST   /v1/devices/  register (upsert) an FCM token for the authenticated user
    DELETE /v1/devices/  remove one of the authenticated user's tokens
    """
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit(key='user', rate='30/h', method='POST', block=True))
    def post(self, request):
        serializer = DeviceTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # A token belongs to one device; re-assign it if another user previously registered it.
        _, created = DeviceToken.objects.update_or_create(
            token=serializer.validated_data['token'],
            defaults={'user': request.user, 'platform': serializer.validated_data['platform']},
        )
        return Response(status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @method_decorator(ratelimit(key='user', rate='30/h', method='DELETE', block=True))
    def delete(self, request):
        serializer = DeviceTokenDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Filtered by user: deleting someone else's or an unknown token is a silent no-op.
        DeviceToken.objects.filter(user=request.user, token=serializer.validated_data['token']).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

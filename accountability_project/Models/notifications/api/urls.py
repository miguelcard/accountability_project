from django.urls import path
from Models.notifications.api.api import DeviceTokenApiView

urlpatterns = [
    path('v1/devices/', DeviceTokenApiView.as_view(), name='device-token'),
]

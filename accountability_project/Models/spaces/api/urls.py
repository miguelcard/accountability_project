from django.urls import path
from Models.spaces.api.api import SpacesApiView

urlpatterns = [
    path('v1/spaces/', SpacesApiView.as_view(), name='habits'),
]
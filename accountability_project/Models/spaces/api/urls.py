from django.urls import path
from Models.spaces.api.api import SpacesApiView, SpacesDetailApiView, SpacesDetailRetrieveWithHabitsApiView, SpaceHabitsApiView

urlpatterns = [
    path('v1/spaces/', SpacesApiView.as_view(), name='spaces'),
    path('v1/spaces/<int:pk>', SpacesDetailRetrieveWithHabitsApiView.as_view(), name='spaces-detail-habits'),
    path('v1/spaces/<int:pk>/simple/', SpacesDetailApiView.as_view(), name='spaces-detail'),
    path('v1/spaces/<int:space_pk>/habits/', SpaceHabitsApiView.as_view(), name='spaces-detail-habits'),
]
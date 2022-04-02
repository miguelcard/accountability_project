from django.urls import path
from Models.spaces.api.api import (SpacesApiView, SpacesDetailApiView, SpacesDetailRetrieveWithHabitsApiView, SpaceHabitsApiView, 
SpaceRoleDeleteApiView, SpaceRoleInviteApiView, SpaceRoleEditApiView)

urlpatterns = [
    path('v1/spaces/', SpacesApiView.as_view(), name='spaces'),
    path('v1/spaces/<int:pk>', SpacesDetailRetrieveWithHabitsApiView.as_view(), name='spaces-detail-habits'),
    path('v1/spaces/<int:pk>/simple/', SpacesDetailApiView.as_view(), name='spaces-detail'),
    path('v1/spaces/<int:space_pk>/habits/', SpaceHabitsApiView.as_view(), name='spaces-detail-habits'),
    path('v1/spaceroles/delete/<int:pk>', SpaceRoleDeleteApiView.as_view(), name='spacerole-delete'),
    path('v1/spaceroles/invite/', SpaceRoleInviteApiView.as_view(), name='spacerole-invite'),
    path('v1/spaceroles/manage/<int:pk>', SpaceRoleEditApiView.as_view(), name='spacerole-edit-delete'),
]
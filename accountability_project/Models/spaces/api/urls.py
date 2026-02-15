from django.urls import path
from Models.spaces.api.api import (SpaceUsersApiView, SpacesApiView, SpacesDetailApiView, SpacesDetailRetrieveWithHabitsApiView, SpaceHabitsApiView, 
SpaceRoleDeleteApiView, SpaceRoleInviteApiView, SpaceRoleEditApiView, SpaceRolesListApiView, SpaceMemberRemoveApiView, CalendarAPIView)

urlpatterns = [
    path('v1/spaces/', SpacesApiView.as_view(), name='spaces'),
    path('v1/spaces/<int:pk>/checkmarks/', CalendarAPIView.as_view(), name="calendar-checkmark-list"),
    path('v1/spaces/<int:pk>', SpacesDetailRetrieveWithHabitsApiView.as_view(), name='spaces-detail'),
    path('v1/spaces/<int:pk>/simple/', SpacesDetailApiView.as_view(), name='spaces-detail-simple'),
    path('v1/spaces/<int:space_pk>/habits/', SpaceHabitsApiView.as_view(), name='spaces-habits-list'),
    path('v1/spaces/<int:space_pk>/spaceroles/', SpaceRolesListApiView.as_view(), name='spaceroles-list'),
    path('v1/spaces/<int:space_pk>/users/', SpaceUsersApiView.as_view(), name='space-users-list'),
    path('v1/spaces/<int:space_pk>/members/<int:user_pk>', SpaceMemberRemoveApiView.as_view(), name='space-member-remove'),
    path('v1/spaceroles/delete/<int:pk>', SpaceRoleDeleteApiView.as_view(), name='spacerole-delete'),
    path('v1/spaceroles/invite/', SpaceRoleInviteApiView.as_view(), name='spacerole-invite'),
    path('v1/spaceroles/manage/<int:pk>', SpaceRoleEditApiView.as_view(), name='spacerole-edit'),
]
from django.urls import path
from Models.groups.api.api import GroupApiView, GroupDetailApiView, GroupGenericApiView

urlpatterns = [
    path('group/', GroupApiView.as_view()),
    path('group/<int:pk>', GroupDetailApiView.as_view()),
    path('groupgeneric/',GroupGenericApiView.as_view()),
    path('groupgeneric/<int:pk>',GroupGenericApiView.as_view())
]
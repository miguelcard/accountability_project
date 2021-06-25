from django.urls import path
from Models.groups.api.api import GroupApiView, GroupDetailApiView, GroupGenericApiView

urlpatterns = [
    path('group/',GroupGenericApiView.as_view()),
    path('group/<int:pk>',GroupGenericApiView.as_view())
]
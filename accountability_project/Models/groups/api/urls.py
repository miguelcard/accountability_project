from django.urls import path
from Models.groups.api.api import GroupGenericApiView, PostGenericApiView

urlpatterns = [
    path('group/',GroupGenericApiView.as_view()),
    path('group/<int:pk>',GroupGenericApiView.as_view()),
    path('post/', PostGenericApiView.as_view()),
    path('post/<int:pk>', PostGenericApiView.as_view())
]
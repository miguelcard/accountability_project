from django.urls import path
from Models.groups.api.api import GroupGenericApiView, PostGenericApiView

urlpatterns = [
    path('v1/groups/',GroupGenericApiView.as_view()),
    path('v1/groups/<int:pk>',GroupGenericApiView.as_view()),
    path('v1/groups/<int:pk>/posts/', PostGenericApiView.as_view()),  
    #path('v1/groups/<int:pk>/posts/<int:pk>', PostGenericApiView.as_view())
]
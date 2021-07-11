from django.urls import path
from Models.users.api.api import UserGenericApiView, UpdateUserWithoutPasswordApiView
from Models.users.views import RegisterAPI, LoginAPI
from knox import views as knox_views

urlpatterns = [
    path('v1/users/', UserGenericApiView.as_view()),
    path('v1/users/<int:pk>', UserGenericApiView.as_view()),
    path('v1/users/update/<int:pk>', UpdateUserWithoutPasswordApiView.as_view()),
    path('v1/register/', RegisterAPI.as_view(), name='register'),
    path('v1/login/', LoginAPI.as_view(), name='login'),
    path('v1/logout/',knox_views.LogoutView.as_view(), name='logout'),
    path('v1/logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall')
]
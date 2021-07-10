from django.urls import path
from Models.users.api.api import UserGenericApiView
from Models.users.views import RegisterAPI, LoginAPI
from knox import views as knox_views

urlpatterns = [
    path('user/', UserGenericApiView.as_view()),
    path('user/<int:pk>', UserGenericApiView.as_view()),
    path('register/', RegisterAPI.as_view(), name='register'),
    path('login/', LoginAPI.as_view(), name='login'),
    path('logout/',knox_views.LogoutView.as_view(), name='logout'),
    path('logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall')
]
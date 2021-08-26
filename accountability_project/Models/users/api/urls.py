from django.urls import path
from Models.users.api.api import LoggedInUserApiView, UserGenericApiView, GetAllUserTagsApiView, GetAllUserLanguagesApiView
from Models.users.views import RegisterAPI, LoginAPI
from knox import views as knox_views

urlpatterns = [
    path('v1.1/user/', LoggedInUserApiView.as_view(), name='user'),
    path('v1/users/tags/', GetAllUserTagsApiView.as_view()),
    path('v1/users/languages/', GetAllUserLanguagesApiView.as_view()),
    path('v1/register/', RegisterAPI.as_view(), name='register'), 
    path('v1/login/', LoginAPI.as_view(), name='login'),          
    path('v1/logout/',knox_views.LogoutView.as_view(), name='logout'),
    path('v1/logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall'),
    path('v1/users/', UserGenericApiView.as_view()), # Only visible to admins
    path('v1/users/<int:pk>', UserGenericApiView.as_view()), # Only visible to admins
]
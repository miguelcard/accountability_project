from django.urls import path
from Models.users.api.api import LoggedInUserApiView, UsernameAndEmailSearchView, UsersAdminApiView, SingleUserAdminApiView, GetAllUserTagsApiView, GetAllUserLanguagesApiView, CheckEmailUsernameView
from Models.users.views import RegisterAPI, LoginAPI
from knox import views as knox_views

urlpatterns = [
    path('v1/user/', LoggedInUserApiView.as_view(), name='user'),
    path('v1/users/tags/', GetAllUserTagsApiView.as_view()),
    path('v1/users/languages/', GetAllUserLanguagesApiView.as_view()),
    path('v1/register/', RegisterAPI.as_view(), name='register'), 
    path('v1/login/', LoginAPI.as_view(), name='login'),          
    path('v1/logout/',knox_views.LogoutView.as_view(), name='logout'),
    path('v1/logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall'),
    path('v1/admin/users/', UsersAdminApiView.as_view()), # Only visible to admins
    path('v1/admin/users/<int:pk>', SingleUserAdminApiView.as_view()), # Only visible to admins
    path('v1/users/usernames-emails/', UsernameAndEmailSearchView.as_view(), name='search-user'),
    path('v1/users/username-or-email-exists/', CheckEmailUsernameView.as_view(), name='search-user'),
]
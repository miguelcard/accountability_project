from django.urls import path
from Models.users.api.api import LoggedInUserApiView, UsernameAndEmailSearchView, UsersAdminApiView, SingleUserAdminApiView, GetAllUserTagsApiView, GetAllUserLanguagesApiView, CheckEmailUsernameView

urlpatterns = [
    path('v1/user/', LoggedInUserApiView.as_view(), name='user'),
    path('v1/users/tags/', GetAllUserTagsApiView.as_view()),
    path('v1/users/languages/', GetAllUserLanguagesApiView.as_view()),
    path('v1/admin/users/', UsersAdminApiView.as_view()), # Only visible to admins
    path('v1/admin/users/<int:pk>', SingleUserAdminApiView.as_view()), # Only visible to admins
    path('v1/users/usernames-emails/', UsernameAndEmailSearchView.as_view(), name='search-user'),
    path('v1/users/username-or-email-exists/', CheckEmailUsernameView.as_view(), name='check-user-exists'),
]
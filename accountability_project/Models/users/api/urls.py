from django.urls import path
from Models.users.api.api import UserGenericApiView
from Models.users.views import RegisterAPI, Login, Logout

urlpatterns = [
    path('user/', UserGenericApiView.as_view()),
    path('user/<int:pk>', UserGenericApiView.as_view()),
    path('register/', RegisterAPI.as_view()),
    path('login/', Login.as_view(), name = 'login'),
    path('logout/', Logout.as_view(), name = 'logout')
]
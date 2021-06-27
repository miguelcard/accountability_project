from django.urls import path
from Models.users.api.api import UserGenericApiView

urlpatterns = [
    path('user/', UserGenericApiView.as_view()),
    path('user/<int:pk>', UserGenericApiView.as_view())
]
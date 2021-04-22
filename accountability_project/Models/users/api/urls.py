from django.urls import path
from Models.users.api.api import user_api_view, user_datail_api_view

urlpatterns = [
    path('user/', user_api_view, name = 'user_api'),
    path('user/<int:pk>', user_datail_api_view, name = 'user_datail_api_view')
]
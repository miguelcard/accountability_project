from django.urls import path
from apps.groups.api.api import group_api_view, group_datail_api_view

urlpatterns = [
    path('group/', group_api_view, name = 'group_api'),
    path('group/<int:pk>', group_datail_api_view, name = 'group_datail_api_view')
]
from django.urls import path
from Models.groups.api.api import GroupApiView, group_api_view, group_detail_api_view

urlpatterns = [
    #path('group/', group_api_view, name = 'group_api'),
    path('group/', GroupApiView.as_view(), name = 'group_api'),
    path('group/<int:pk>', group_detail_api_view, name = 'group_detail_api_view')
]
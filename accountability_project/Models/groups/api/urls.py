from django.urls import path
from Models.groups.api.api import GroupApiView, GroupDetailApiView

urlpatterns = [
    path('group/', GroupApiView.as_view()),
    path('group/<int:pk>', GroupDetailApiView.as_view())
    #path('group/', group_api_view, name = 'group_api'),
    #path('group/<int:pk>', group_detail_api_view, name = 'group_detail_api_view')
]
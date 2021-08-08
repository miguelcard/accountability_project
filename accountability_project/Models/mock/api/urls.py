from django.urls import path
from Models.mock.api.api import HabitDetailView, UserDetailView, SpaceDetailView

urlpatterns = [
    path('v1/mock/habit/', HabitDetailView.as_view()),
    path('v1/mock/user/', UserDetailView.as_view()),
    path('v1/mock/space/', SpaceDetailView.as_view()),
    


    #path('v1/habits/<int:pk>', HabitGenericApiView.as_view()),
]

from django.urls import path
from Models.mock.api.api import MyOwnView

urlpatterns = [
    path('v1/mock/', MyOwnView.as_view()),


    #path('v1/habits/<int:pk>', HabitGenericApiView.as_view()),
]

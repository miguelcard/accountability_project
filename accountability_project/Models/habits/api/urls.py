from django.urls import path
from Models.habits.api.api import HabitGenericApiView

urlpatterns = [
    path('v1/habits/', HabitGenericApiView.as_view()),
    path('v1/habits/<int:pk>', HabitGenericApiView.as_view()),
]

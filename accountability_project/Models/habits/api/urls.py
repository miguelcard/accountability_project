from django.urls import path
from Models.habits.api.api import HabitGenericApiView

urlpatterns = [
    path('habit/', HabitGenericApiView.as_view()),
    path('habit/<int:pk>', HabitGenericApiView.as_view()),
]

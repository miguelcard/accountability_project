from django.urls import path
from Models.habits.api.api import Habit_api_view, habit_datail_api_view

urlpatterns = [
    path('habit/', Habit_api_view, name='habit_api'),
    path('habit/<int:pk>', habit_datail_api_view, name='habit_datail_api_view'),
]

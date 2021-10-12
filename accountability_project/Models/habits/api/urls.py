from Models.habits.api.api import RecurrentHabitApiView, RecurrentHabitDetailApiView, GoalApiView, GoalDetailApiView, AllHabitsApiView
from django.urls import path

urlpatterns = [
    path('v1/habits/', AllHabitsApiView.as_view(), name='habits'),
    path('v1/habits/<int:pk>', AllHabitsApiView.as_view(), name='habits-detail'),
    path('v1/habits/recurrent/', RecurrentHabitApiView.as_view(), name='recurrent'),
    path('v1/habits/recurrent/<int:pk>', RecurrentHabitDetailApiView.as_view(), name='recurrent-detail'),
    path('v1/habits/goals/', GoalApiView.as_view(), name='goal'),
    path('v1/habits/goals/<int:pk>', GoalDetailApiView.as_view(), name='goal-detail'),
]

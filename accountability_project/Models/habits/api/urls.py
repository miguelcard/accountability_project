from Models.habits.api.api import RecurrentHabitApiView
from django.urls import path

urlpatterns = [
    path('v1/habits/', RecurrentHabitApiView.as_view(), name='habits'),
    # path('v1/habits/', HabitGenericApiView.as_view()),
    # path('v1/habits/<int:pk>', HabitGenericApiView.as_view()),

    # Goal paths:
    # path('v1/habits/', HabitGenericApiView.as_view()), #shows all types of habits/goals, see https://app.clickup.com/t/125e4t3
    # path('v1/habits/:type', view), # type in this case can be recurrent or goal ... or in two different urls? 
    # path('v1/habits/<int:pk>', HabitGenericApiView.as_view()),  # gets specific habit
]

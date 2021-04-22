from django.urls import path
from Models.habits.api.api import Habit_api_view, habit_datail_api_view
from Models.habits.api.api import Start_day_api_view, Start_day_datail_api_view
from Models.habits.api.api import Finish_day_api_view, Finish_day_datail_api_view


urlpatterns = [
    path('habit/', Habit_api_view, name='habit_api'),
    path('habit/<int:pk>', habit_datail_api_view, name='habit_datail_api_view'),
    path('startday/', Start_day_api_view, name='startday_api'),
    path('startday/<int:pk>', Start_day_datail_api_view, name='startday_datail_api_view'),
    path('finishday/', Finish_day_api_view, name='finishday_api'),
    path('finishday/<int:pk>', Finish_day_datail_api_view, name='finishday_datail_api_view')
]

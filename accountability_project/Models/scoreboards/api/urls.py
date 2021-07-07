from django.urls import path
from Models.scoreboards.api.api import ScoreboardGenericApiView

urlpatterns = [
    path('scoreboard/', ScoreboardGenericApiView.as_view()),
    path('scoreboard/<int:pk>', ScoreboardGenericApiView.as_view())
]
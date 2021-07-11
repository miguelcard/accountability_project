from django.urls import path
from Models.scoreboards.api.api import ScoreboardGenericApiView

urlpatterns = [
    path('v1/scoreboards/', ScoreboardGenericApiView.as_view()),
    path('v1/scoreboards/<int:pk>', ScoreboardGenericApiView.as_view())
]
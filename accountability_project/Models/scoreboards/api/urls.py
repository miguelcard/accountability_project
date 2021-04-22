from django.urls import path
from Models.scoreboards.api.api import score_board_api_view, score_board_datail_api_view

urlpatterns = [
    path('scoreboard/', score_board_api_view, name = 'score_board_api'),
    path('scoreboard/<int:pk>', score_board_datail_api_view, name = 'score_board_datail_api_view')
]
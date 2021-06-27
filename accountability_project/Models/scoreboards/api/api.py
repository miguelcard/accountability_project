from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from Models.scoreboards.models import Scoreboard
from Models.scoreboards.api.serializers import ScoreboardSerializer

""" ---------views for scoreboards--------"""

@api_view(['GET', 'POST'])
def score_board_api_view(request):

    if request.method == 'GET':
        score_board = Scoreboard.objects.all()
        score_board_serializer = ScoreboardSerializer(score_board, many=True)
        return Response(score_board_serializer.data, status= status.HTTP_200_OK)

    elif request.method == 'POST':
        score_board_serializer = ScoreboardSerializer(data = request.data)
        if score_board_serializer.is_valid():
            score_board_serializer.save()
            return Response(score_board_serializer.data, status= status.HTTP_200_OK)
        return Response(score_board_serializer.errors, status= status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def score_board_detail_api_view(request, pk=None):
    score_board = Scoreboard.objects.filter(id = pk).first()

    if score_board:
        if request.method == 'GET':
            score_board_serializer = ScoreboardSerializer(score_board)
            return Response(score_board_serializer.data, status= status.HTTP_200_OK)

        elif request.method == 'PUT':
            score_board_serializer = ScoreboardSerializer(score_board, data = request.data)
            if score_board_serializer.is_valid():
                score_board_serializer.save()
                return Response(score_board_serializer.data, status= status.HTTP_200_OK)
            return Response(score_board_serializer.errors, status= status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            score_board.delete()
            return Response({'Message':'scoreboard has been delete'}, status= status.HTTP_200_OK)

    return Response({'Message':'scoreboard not found'}, status= status.HTTP_400_BAD_REQUEST)

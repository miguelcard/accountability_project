from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.habits.models import Habit
from apps.habits.api.serializers import HabitSerializer


@api_view(['GET', 'POST'])
def Habit_api_view(request):
    """ api view setup"""
    if request.method == 'GET':
        habits = Habit.objects.all()
        habit_serializer = HabitSerializer(habits, many=True)
        return Response(habit_serializer.data, status= status.HTTP_200_OK)

    elif request.method == 'POST':
        habit_serializer = HabitSerializer(data = request.data)
        if habit_serializer.is_valid():
            habit_serializer.save()
            return Response(habit_serializer.data, status= status.HTTP_200_OK)
        return Response(habit_serializer.errors, status= status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def habit_datail_api_view(request, pk=None):
    habit = Habit.objects.filter(id = pk).first()

    if habit:
        if request.method == 'GET':
            habit_serializer = HabitSerializer(habit)
            return Response(habit_serializer.data, status= status.HTTP_200_OK)

        elif request.method == 'PUT':
            habit_serializer = HabitSerializer(habit, data = request.data)
            if habit_serializer.is_valid():
                habit_serializer.save()
                return Response(habit_serializer.data, status= status.HTTP_200_OK)
            return Response(habit_serializer.errors, status= status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            habit.delete()
            return Response({'Message':'habit has been delete'}, status= status.HTTP_200_OK)

    return Response({'Message':'habit not found'}, status= status.HTTP_400_BAD_REQUEST)
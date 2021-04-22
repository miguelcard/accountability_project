from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from Models.habits.models import Habit, StartDay, FinishDay
from Models.habits.api.serializers import HabitSerializer, StartDaySerializer, FinishDaySerializer



""" ---------views for habits--------"""


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


""" ---------views for startdays--------"""


@api_view(['GET', 'POST'])
def Start_day_api_view(request):
    """ api view setup"""
    if request.method == 'GET':
        start_day = StartDay.objects.all()
        start_day_serializer = StartDaySerializer(start_day, many=True)
        return Response(start_day_serializer.data, status= status.HTTP_200_OK)

    elif request.method == 'POST':
        start_day_serializer = StartDaySerializer(data = request.data)
        if start_day_serializer.is_valid():
            start_day_serializer.save()
            return Response(start_day_serializer.data, status= status.HTTP_200_OK)
        return Response(start_day_serializer.errors, status= status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def Start_day_datail_api_view(request, pk=None):
    start_day = StartDay.objects.filter(id = pk).first()

    if start_day:
        if request.method == 'GET':
            start_day_serializer = StartDaySerializer(start_day)
            return Response(start_day_serializer.data, status= status.HTTP_200_OK)

        elif request.method == 'PUT':
            start_day_serializer = StartDaySerializer(start_day, data = request.data)
            if start_day_serializer.is_valid():
                start_day_serializer.save()
                return Response(start_day_serializer.data, status= status.HTTP_200_OK)
            return Response(start_day_serializer.errors, status= status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            start_day.delete()
            return Response({'Message':'Start day has been delete'}, status= status.HTTP_200_OK)

    return Response({'Message':'start day not found'}, status= status.HTTP_400_BAD_REQUEST)



""" ---------views for finishdays--------"""


@api_view(['GET', 'POST'])
def Finish_day_api_view(request):
    """ api view setup"""
    if request.method == 'GET':
        finish_day = FinishDay.objects.all()
        finish_day_serializer = FinishDaySerializer(finish_day, many=True)
        return Response(finish_day_serializer.data, status= status.HTTP_200_OK)

    elif request.method == 'POST':
        finish_day_serializer = FinishDaySerializer(data = request.data)
        if finish_day_serializer.is_valid():
            finish_day_serializer.save()
            return Response(finish_day_serializer.data, status= status.HTTP_200_OK)
        return Response(finish_day_serializer.errors, status= status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def Finish_day_datail_api_view(request, pk=None):
    finish_day = FinishDay.objects.filter(id = pk).first()

    if finish_day:
        if request.method == 'GET':
            finish_day_serializer = FinishDaySerializer(finish_day)
            return Response(finish_day_serializer.data, status= status.HTTP_200_OK)

        elif request.method == 'PUT':
            finish_day_serializer = FinishDaySerializer(finish_day, data = request.data)
            if finish_day_serializer.is_valid():
                finish_day_serializer.save()
                return Response(finish_day_serializer.data, status= status.HTTP_200_OK)
            return Response(finish_day_serializer.errors, status= status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            finish_day.delete()
            return Response({'Message':'Finish day has been delete'}, status= status.HTTP_200_OK)

    return Response({'Message':'finish day not found'}, status= status.HTTP_400_BAD_REQUEST)
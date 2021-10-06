from django.http import request, response
from rest_framework import serializers
from rest_framework.serializers import Serializer
from Models.habits.api.serializers import RecurrentHabitSerializerToRead, RecurrentHabitSerializerToWrite, GoalSerializerToRead, GoalSerializerToWrite
from Models.habits.models import BaseHabit, RecurrentHabit, Goal
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from itertools import chain

""" ---------views for habits--------"""

""" ---------views for recurrent habits-------"""

# GET & POST
class RecurrentHabitApiView(generics.ListCreateAPIView): 
    serializer_class = RecurrentHabitSerializerToRead

    def get_queryset(self):
        return RecurrentHabit.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if(self.request is not None and self.request.method == 'POST'):
            return RecurrentHabitSerializerToWrite
        return RecurrentHabitSerializerToRead
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# PUT, PATCH, DELETE & GET (detailed)
class RecurrentHabitDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RecurrentHabitSerializerToWrite

    def get_queryset(self):
        return RecurrentHabit.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if(self.request is not None and self.request.method == 'GET'):
            return RecurrentHabitSerializerToRead
        return RecurrentHabitSerializerToWrite

""" ---------views for Goals-------"""

# GET & POST
class GoalApiView(generics.ListCreateAPIView): 
    serializer_class = GoalSerializerToRead

    def get_queryset(self):
        return Goal.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if(self.request is not None and self.request.method == 'POST'):
            return GoalSerializerToWrite
        return GoalSerializerToRead
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# PUT, PATCH, DELETE & GET (detailed)
class GoalDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GoalSerializerToRead

    def get_queryset(self):
        return Goal.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if(self.request is not None and self.request.method == 'GET'):
            return GoalSerializerToRead
        return GoalSerializerToWrite

# GET    MAYBE THE POST DOES NOT MAKE MUCH SENSE WITH THIS ONE 
class AllHabitsApiView(generics.GenericAPIView): 

    filter_backends = [OrderingFilter]
    ordering_fields = ['id', 'title', 'created_at', 'updated_at', 'type']

    def get(self, request, *args, **kwargs):
        context = {"request": request,}
        # All Habits queryset
        all_habits = BaseHabit.objects.filter(owner=self.request.user).select_subclasses()
        filtered_habits = self.filter_queryset(all_habits)
        
        response_data = []
        for habit in filtered_habits:
            if habit.type == "recurrent":
                specific_serializer = RecurrentHabitSerializerToRead(habit, context=context)
            else:
                specific_serializer = GoalSerializerToRead(habit, context=context)
            response_data.append(specific_serializer.data)
         
        return Response(response_data)
        

# PUT, PATCH, DELETE & GET (detailed) # MAYBE PUT AND PATCH NO SENSE ?? OR YES?
# class AllHabitsDetailApiView(generics.RetrieveUpdateDestroyAPIView):
#     serializer_class = RecurrentHabitSerializerToWrite

#     def get_queryset(self):
#         return RecurrentHabit.objects.filter(owner=self.request.user)

#     def get_serializer_class(self):
#         if(self.request is not None and self.request.method == 'GET'):
#             return HabitSerializerToRead
#         return HabitSerializerToWrite

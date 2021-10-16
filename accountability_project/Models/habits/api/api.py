from Models.habits.api.serializers import RecurrentHabitSerializerToRead, RecurrentHabitSerializerToWrite, GoalSerializerToRead, GoalSerializerToWrite, HabitTagSerializer
from Models.habits.models import BaseHabit, RecurrentHabit, Goal, HabitTag
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from Models.habits.api.pagination import AllHabitsPagination, HabitTagsPagination

""" ---------views for habits--------"""

""" ---------views for recurrent habits-------"""

# GET & POST
class RecurrentHabitApiView(generics.ListCreateAPIView): 
    pagination_class = AllHabitsPagination
    serializer_class = RecurrentHabitSerializerToRead
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_fields = ['title', 'time_frame', 'times', 'tags__name'] # Space (id), 
    ordering_fields = ['id', 'title', 'created_at', 'updated_at', 'time_frame', 'times', 'tags__name']  
    search_fields = ['title', 'description', 'time_frame', 'times', 'tags__name'] # Space

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
    pagination_class = AllHabitsPagination
    serializer_class = GoalSerializerToRead
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_fields = ['title', 'start_date', 'finish_date', 'tags__name'] # Space (id), Milestone_name
    ordering_fields = ['id', 'title', 'created_at', 'updated_at', 'start_date', 'finish_date', 'tags__name']  
    search_fields = ['title', 'description', 'start_date', 'finish_date', 'tags__name'] # Space, Milestone_name

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


""" ---------view for both Recurrent Habits and Goals-------"""
# GET & GET (detailed) 
class AllHabitsApiView(generics.GenericAPIView): 
    pagination_class = AllHabitsPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_fields = ['type', 'title', 'recurrenthabit__times', 'recurrenthabit__time_frame', 'goal__start_date', 'goal__finish_date', 'tags__name'] # Space (id),
    ordering_fields = ['id', 'title', 'created_at', 'updated_at', 'type', 'recurrenthabit__times', 'recurrenthabit__time_frame', 'goal__start_date', 'goal__finish_date', 'tags__name']
    search_fields = ['title', 'description', 'type', 'recurrenthabit__times', 'recurrenthabit__time_frame', 'tags__name'] # Space
    
    def get(self, request, *args, **kwargs):
        context = {"request": request,}
        pk = kwargs.get('pk')
        # Get specific habit
        if pk:
            try:
                habit = BaseHabit.objects.get(pk=pk)
                if habit.type == 'recurrent':
                    habit_specific = RecurrentHabit.objects.get(pk=pk)
                    habit_serializer = RecurrentHabitSerializerToRead(habit_specific, context=context)
                else:
                    habit_specific = Goal.objects.get(pk=pk)
                    habit_serializer = GoalSerializerToRead(habit_specific, context=context) 
            except BaseHabit.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            return Response(habit_serializer.data)
        # Get all habits
        else: 
            # All Habits queryset
            all_habits = BaseHabit.objects.filter(owner=self.request.user).select_subclasses()
            filtered_habits = self.filter_queryset(all_habits)
            page = self.paginate_queryset(filtered_habits)

            query_results = page if page is not None else filtered_habits
            response_data = []
            for habit in query_results:
                if habit.type == 'recurrent':
                    specific_serializer = RecurrentHabitSerializerToRead(habit, context=context)
                else:
                    specific_serializer = GoalSerializerToRead(habit, context=context)
                response_data.append(specific_serializer.data) 
                
            return self.get_paginated_response(response_data) if page is not None else Response(response_data)

# Get view to show all existent tags for user to choose from
class GetAllHabitTagsApiView(generics.ListAPIView):
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ['name']  
    search_fields = ['name'] 
    queryset = HabitTag.objects.all()
    serializer_class = HabitTagSerializer
    pagination_class = HabitTagsPagination
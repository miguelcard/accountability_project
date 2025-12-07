from rest_framework.exceptions import NotFound
from Models.habits.api.serializers import RecurrentHabitSerializerToPatch, RecurrentHabitSerializerToRead, RecurrentHabitSerializerToWrite, GoalSerializerToRead, GoalSerializerToWrite, HabitTagSerializer, CheckMarkNestedSerializer, MilestoneNestedSerializer
from Models.habits.models import BaseHabit, RecurrentHabit, Goal, HabitTag, CheckMark, Milestone
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from Models.habits.api.pagination import AllHabitsPagination, HabitTagsPagination, CheckmarksPagination
from django.shortcuts import get_object_or_404
from Models.habits.api.permissions import IsOwnerOfParentHabit, UserBelongsToHabitSpaces
from utils.exceptionhandlers import BusinessLogicConflict
from rest_framework.permissions import IsAuthenticated

""" ---------views for habits--------"""

""" ---------views for recurrent habits-------"""

# GET & POST
class RecurrentHabitApiView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, UserBelongsToHabitSpaces]
    pagination_class = AllHabitsPagination
    serializer_class = RecurrentHabitSerializerToRead
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_fields = ['title', 'time_frame', 'times', 'tags__name', 'spaces__name', 'spaces__id'] 
    ordering_fields = ['id', 'title', 'created_at', 'updated_at', 'time_frame', 'times', 'tags__name', 'spaces__id']  
    search_fields = ['title', 'description', 'time_frame', 'times', 'tags__name', 'spaces__name'] 

    def get_queryset(self):
        return RecurrentHabit.objects.filter(owner=self.request.user.id)

    def get_serializer_class(self):
        if(self.request is not None and self.request.method == 'POST'):
            return RecurrentHabitSerializerToWrite
        return RecurrentHabitSerializerToRead
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# PUT, PATCH, DELETE & GET (detailed)
class RecurrentHabitDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, UserBelongsToHabitSpaces]
    serializer_class = RecurrentHabitSerializerToWrite

    def get_queryset(self):
        return RecurrentHabit.objects.filter(owner=self.request.user.id)

    def get_serializer_class(self):
        if(self.request is not None and self.request.method == 'GET'):
            return RecurrentHabitSerializerToRead
        if(self.request is not None and self.request.method == 'PUT'): # ensure required fields in PUT
            return RecurrentHabitSerializerToWrite
        return RecurrentHabitSerializerToPatch # when patching no need to ensure all the required fields are passed

""" ---------views for Goals-------"""

# GET & POST
class GoalApiView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, UserBelongsToHabitSpaces]
    serializer_class = GoalSerializerToRead
    pagination_class = AllHabitsPagination 
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_fields = ['title', 'start_date', 'finish_date', 'tags__name', 'spaces__name', 'spaces__id', 'milestones__name'] 
    ordering_fields = ['id', 'title', 'created_at', 'updated_at', 'start_date', 'finish_date', 'tags__name']  
    search_fields = ['title', 'description', 'start_date', 'finish_date', 'tags__name', 'spaces__name', 'milestones__name'] 

    def get_queryset(self):
        return Goal.objects.filter(owner=self.request.user.id)

    def get_serializer_class(self):
        if(self.request is not None and self.request.method == 'POST'):
            return GoalSerializerToWrite
        return GoalSerializerToRead

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# PUT, PATCH, DELETE & GET (detailed)
class GoalDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, UserBelongsToHabitSpaces]
    serializer_class = GoalSerializerToRead

    def get_queryset(self):
        return Goal.objects.filter(owner=self.request.user.id)

    def get_serializer_class(self):
        if(self.request is not None and self.request.method == 'GET'):
            return GoalSerializerToRead
        return GoalSerializerToWrite
    

# GET & GET (detailed) 
class AllHabitsApiView(generics.GenericAPIView): 
    """
    View for both Recurrent Habits and Goals.
    If no parameter is sent it will return all the Habits and Goals belonging to the authenticated user
    If the {id} parameter is sent, only the Habit/Goal with that id will be returned.
    """
    pagination_class = AllHabitsPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_fields = ['type', 'title', 'recurrenthabit__times', 'recurrenthabit__time_frame', 'goal__start_date', 'goal__finish_date', 'tags__name', 'owner__id', 'owner__username', 'spaces__name', 'spaces__id'] 
    ordering_fields = ['id', 'title', 'created_at', 'updated_at', 'type', 'recurrenthabit__times', 'recurrenthabit__time_frame', 'goal__start_date', 'goal__finish_date', 'tags__name', 'owner__id', 'owner__username']
    search_fields = ['title', 'description', 'type', 'recurrenthabit__times', 'recurrenthabit__time_frame', 'tags__name', 'owner__username', 'spaces__name'] 
    
    def get(self, request, *args, **kwargs):
        context = {"request": request,}
        pk = kwargs.get('pk')
        # Get specific habit
        if pk:
            try:
                habit = get_object_or_404(BaseHabit, owner=self.request.user, pk=pk)
                if habit.type == 'recurrent':
                    habit_specific = get_object_or_404(RecurrentHabit, owner=self.request.user, pk=pk)
                    habit_serializer = RecurrentHabitSerializerToRead(habit_specific, context=context)
                elif habit.type == 'goal':
                    habit_specific = get_object_or_404(Goal, owner=self.request.user, pk=pk)
                    habit_serializer = GoalSerializerToRead(habit_specific, context=context) 
                else:
                    raise BusinessLogicConflict(detail=('The habit with id: ', pk,' does not have its Type set to either Recurrent or Goal'))
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
        

# GET
class GetAllHabitTagsApiView(generics.ListAPIView):
    """
    Get view to show all existent Tags for user to choose from
    """
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ['name']  
    search_fields = ['name'] 
    queryset = HabitTag.objects.all()
    serializer_class = HabitTagSerializer
    pagination_class = HabitTagsPagination

""" ---------views for Checkmarks of a Habit -------"""

# GET & POST, filterable by date in parameters
class CheckmarksApiView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOfParentHabit]
    serializer_class = CheckMarkNestedSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_fields = ['status', 'date']
    ordering_fields = ['status', 'date', 'created_at', 'updated_at']  
    search_fields = ['id', 'date', 'status'] 

    def get_queryset(self, *args, **kwargs): 
        habit_id = self.kwargs.get("habit_pk")
        habit = get_object_or_404(BaseHabit, id=habit_id, owner=self.request.user)
        return CheckMark.objects.all().select_related('habit').filter(habit=habit, habit__owner=self.request.user)

# same class as above but with pagination
class CheckmarksApiViewWithPagination(CheckmarksApiView):
    pagination_class = CheckmarksPagination 

# PUT, PATCH, DELETE & GET (detailed)
class CheckmarksDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOfParentHabit]
    serializer_class = CheckMarkNestedSerializer

    def get_queryset(self, *args, **kwargs): 
        habit_id = self.kwargs.get("habit_pk")
        try:
            habit = BaseHabit.objects.get(id=habit_id)
        except BaseHabit.DoesNotExist:
            raise NotFound('A habit with this id does not exist')
        return CheckMark.objects.all().select_related('habit').filter(habit=habit, habit__owner=self.request.user.id)

""" ---------views for Milestones of a Goal -------"""

# GET & POST
class MilestonesApiView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOfParentHabit]
    serializer_class = MilestoneNestedSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_fields = ['name', 'date', 'status']
    ordering_fields = ['name', 'status', 'date', 'created_at', 'updated_at']  
    search_fields = ['name', 'description', 'id', 'date', 'status'] 

    def get_queryset(self, *args, **kwargs): 
        habit_id = self.kwargs.get("habit_pk")
        try:
            habit = Goal.objects.get(id=habit_id)
        except Goal.DoesNotExist:
            raise NotFound('A Goal with this id does not exist')
        return Milestone.objects.all().select_related('habit').filter(habit=habit, habit__owner=self.request.user)

# same class as above but with pagination
class MilestonesApiViewWithPagination(MilestonesApiView):
    pagination_class = CheckmarksPagination  

# PUT, PATCH, DELETE & GET (detailed)
class MilestonesDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOfParentHabit]
    serializer_class = MilestoneNestedSerializer

    def get_queryset(self, *args, **kwargs): 
        habit_id = self.kwargs.get("habit_pk")
        try:
            habit = Goal.objects.get(id=habit_id)
        except Goal.DoesNotExist:
            raise NotFound('A Goal with this id does not exist')
        return Milestone.objects.all().select_related('habit').filter(habit=habit, habit__owner=self.request.user)
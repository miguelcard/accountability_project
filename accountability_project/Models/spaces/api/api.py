from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import generics, serializers
from Models.spaces.models import Space, SpaceRole
from Models.spaces.api.serializers import SpaceSerializer, SpaceSerializerToReadWithHabits, SpaceRoleSerializer
from django.db.models import Q
from Models.spaces.api.pagination import SpacesPagination, SpaceHabitsPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from Models.habits.models import BaseHabit
from Models.habits.api.serializers import GoalSerializerToRead, RecurrentHabitSerializerToRead
from rest_framework.response import Response
from Models.spaces.api.permissions import IsSpaceAdminOrReadOnly

""" ---------views for Spaces--------"""

# GET & POST
class SpacesApiView(generics.ListCreateAPIView):
    """
    Lists Spaces where current user belongs and Creates Spaces with current user as creator
    """
    serializer_class = SpaceSerializer
    pagination_class = SpacesPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_fields = ['creator__username', 'creator__name', 'name', 'description', 'members__username', 'tags__name', 'spaceroles__member__username', 'spaceroles__role']  # members_username is the same as spacerole__member__username
    ordering_fields = ['id', 'creator__username', 'creator__name', 'name', 'created_at', 'updated_at', 'tags__name', 'members_count', 'habits_count'] 
    search_fields = ['name', 'tags__name', 'creator__username', 'tags__name', 'description', 'members__username', 'members__name']

    def get_queryset(self):
        return Space.objects.annotate(members_count=Count('members', distinct=True)).annotate(habits_count=Count('space_habits', distinct=True)).filter(Q(creator=self.request.user) | Q(members=self.request.user)).prefetch_related('members')

    def perform_create(self, serializer):
        # adds logged in user as creator of the space
        space = serializer.save(creator=self.request.user)
        # creates a role connection of the user and space as admin
        SpaceRole.objects.create(role='admin', member=self.request.user, space=space)
        
# GET (detailed) 
class SpacesDetailRetrieveWithHabitsApiView(generics.RetrieveAPIView):
    """
    Retrieves an specific Space if the user is the creator or a member of it, the Space habits are shown in detail in a nested seializer
    """
    serializer_class = SpaceSerializerToReadWithHabits # This could be another serializer class with more details in the "to_representation method" if you choose it as the endpoint for PUT

    def get_queryset(self, *args, **kwargs): 
        return Space.objects.annotate(members_count=Count('members', distinct=True)).annotate(habits_count=Count('space_habits', distinct=True)).filter(Q(creator=self.request.user) | Q(members=self.request.user)).prefetch_related('members')

# GET (detailed), PUT, PATCH
class SpacesDetailApiView(generics.RetrieveUpdateAPIView, SpacesDetailRetrieveWithHabitsApiView): 
    """
    Retrieves an specific Space if the user is the creator or a member of it, serializer shows a simple representation of the space
    """
    # permission_classes = [IsAuthenticated, IsSpaceAdminOrReadOnly] # We will let all members edit things like the title and description of the space
    serializer_class = SpaceSerializer 

# GET
class SpaceHabitsApiView(generics.GenericAPIView):
    """
    Lists all habits from a Space, both recurrent ones and goals
    """
    pagination_class = SpaceHabitsPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_fields = ['type', 'title', 'recurrenthabit__times', 'recurrenthabit__time_frame', 'goal__start_date', 'goal__finish_date', 'tags__name', 'owner__id', 'owner__username'] 
    ordering_fields = ['id', 'title', 'created_at', 'updated_at', 'type', 'recurrenthabit__times', 'recurrenthabit__time_frame', 'goal__start_date', 'goal__finish_date', 'tags__name', 'owner__id', 'owner__username']
    search_fields = ['title', 'description', 'type', 'recurrenthabit__times', 'recurrenthabit__time_frame', 'tags__name', 'owner__username'] 

    def get(self, request, *args, **kwargs):
        context = {"request": request,}
        space_id = self.kwargs.get("space_pk")
        space = get_object_or_404(Space, id=space_id, members=self.request.user)
        all_habits = BaseHabit.objects.filter(spaces=space).select_subclasses()
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
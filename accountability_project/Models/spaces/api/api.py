import logging
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import generics, status
from Models.spaces.models import Space, SpaceRole
from Models.users.models import User
from Models.spaces.api.serializers import SimpleUserSerializer, SpaceSerializer, SpaceSerializerToReadWithHabitsAndMembers, SpaceRoleSerializer, SpaceRoleSerializerForEdition
from django.db.models import Q
from Models.spaces.api.pagination import SpacesPagination, SpaceHabitsPagination, GenericPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from Models.habits.models import BaseHabit
from Models.habits.api.serializers import GoalSerializerToRead, RecurrentHabitSerializerToRead
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from Models.spaces.api.permissions import BelongsToSpaceFromSpaceRole, HasEqualOrHigherRoleAsNewUser, IsSpaceAdminWhereSpaceRoleBelongsOrReadOnly
from rest_framework.exceptions import NotFound
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

logger = logging.getLogger(__name__)

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
        return Space.objects.annotate(members_count=Count('members', distinct=True)).annotate(habits_count=Count('space_habits', distinct=True)).filter(Q(members=self.request.user)).prefetch_related('members')

    def perform_create(self, serializer):
        # adds logged in user as creator of the space
        try:
            space = serializer.save(creator=self.request.user)
            logger.info(f'saving new created space {space.id}')
            # creates a role connection of the user and space as admin
            SpaceRole.objects.create(role='admin', member=self.request.user, space=space)
        except ValidationError as error:
            logger.info(f'space could not be created because it exceeds the max amount of spaces a user can create, user id: {self.request.user}')
            raise DRFValidationError({"errors": error.message_dict})

        
# GET (detailed) 
class SpacesDetailRetrieveWithHabitsApiView(generics.RetrieveAPIView):
    """
    Retrieves an specific Space if the user is the creator or a member of it, the Space habits are shown in detail in a nested seializer
    """
    serializer_class = SpaceSerializerToReadWithHabitsAndMembers # This could be another serializer class with more details in the "to_representation method" if you choose it as the endpoint for PUT

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

        return response_data
            
   
# DELETE
class SpaceRoleDeleteApiView(generics.GenericAPIView):
    """
    Unlinks a user from a space by deleting the space role associated with it
    also changes user if he was the creator of the space
    unlinks all habits from that user in that space
    deletes space IF the space has no more members in it
    """
    @transaction.atomic
    def delete(self, request, pk=None):
        user = self.request.user
        space = get_object_or_404(Space, pk=pk)
        try:
            # query if user is member
            space_role = SpaceRole.objects.get(space__id=space.id, member=user.id)
        except SpaceRole.DoesNotExist:
            raise NotFound('User does not belong to the Space')
        
        # TODO for now is not needed to pass the "admin" role to another user if the unlinked user was the ONLY admin 
         
        space_role.delete()
        logger.info(f'space role deleted for user with id: {user.id} username: {user.username} and space with id: {space.id} name: {space.name}')
        self.unlink_habits(space, user, True)

        if not space.members.all():
            logger.info(f'Deleting space which has no more members, space id: "{space.id}" space name: "{space.name}"')
            space.delete()
            # nothing else to do
            return Response(status=status.HTTP_204_NO_CONTENT)
        

        if space.creator == self.request.user:
            logger.info(f'Removing the creator role from user with id: {user.id} username: {user.username} in the space with id: {space.id} name: {space.name}')
            space.creator = None
            space.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


    # The delete_habits tag is a boolean, when set to true, deletes the habit and its checkmarks, for now thats gonna be the behaviour to KISS
    def unlink_habits(self, space, user, delete_habits):

        user_habits = user.habits.all()
        space_habits = space.space_habits.all()

        intersection_habits = list(set(user_habits).intersection(space_habits))

        for habit in intersection_habits:
            if delete_habits:
                habit.delete()
                continue
            habit.spaces.remove(space)
            habit.save()

# POST
class SpaceRoleInviteApiView(generics.CreateAPIView):
    """
    Creates a Spacerole / a role for a user in a space, requested by an existing user of
    that space, i.e. the endpoint where one user adds another one to the space
    """
    permission_classes = [IsAuthenticated, BelongsToSpaceFromSpaceRole, HasEqualOrHigherRoleAsNewUser]
    serializer_class = SpaceRoleSerializer

    # throw custom error message to the GUI (but error is thrown first from the serializer in case in happens, this is build for extra security)
    def perform_create(self, serializer):
        try:
            spaceRole = serializer.save()
            logger.info(f'saving new space role for invited user {spaceRole.member.username} on space {spaceRole.space.id}')
        except ValidationError as error:
            logger.info(f'spaceRole could not be created because it invited user exceeds the max amount of spaces he can belong to')
            raise DRFValidationError({"errors": error.message_dict})

# PUT, PATCH
class SpaceRoleEditApiView(generics.UpdateAPIView):
    """
    admin roles of an Space can edit a member's role (update SpaceRole role)
    """
    permission_classes = [IsAuthenticated, IsSpaceAdminWhereSpaceRoleBelongsOrReadOnly]
    serializer_class = SpaceRoleSerializer

    def get_queryset(self):
        # below sample code returns all the SpaceRoles that belong to a Space where the request user is an admin, 
        # but it can be replaced by IsSpaceAdminWhereSpaceRoleBelongsOrReadOnly, the only difference is that permission class writes custom error message
        # return SpaceRole.objects.filter(space__in = Space.objects.filter(spaceroles__member=self.request.user, spaceroles__role='admin'))
        return SpaceRole.objects.all()

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request is not None and (self.request.method == 'PUT' or self.request.method == 'PATCH'):
            serializer_class = SpaceRoleSerializerForEdition
        return serializer_class

# GET
class SpaceRolesListApiView(generics.ListAPIView):
    """
    Gets list of all the spaceroles from a space where user belongs
    """
    serializer_class = SpaceRoleSerializer
    pagination_class = GenericPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_fields = ['role', 'member__id', 'member__username'] 
    ordering_fields = ['id', 'role', 'member__username', 'member__id', 'member__name']
    search_fields = ['id', 'role', 'member__username', 'member__id', 'member__name'] 

    def get_queryset(self):
        space_id = self.kwargs.get("space_pk")
        logger.info(f' Get all roles from space with id: {space_id}')
        space = get_object_or_404(Space, id=space_id, members=self.request.user)
        logger.info(f' Retrieving all roles for space with id: {space_id} and name: {space.name}')
        return space.spaceroles.all()

# GET
class SpaceUsersApiView(generics.ListAPIView):
    """
    Gets list of all the users from the Space.
    """
    serializer_class = SimpleUserSerializer
    pagination_class = GenericPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    # filter_fields = [] 
    ordering_fields = [
        "username",
        "email",
        "is_active",
        "updated_at",
        ]
    # search_fields = [] 

    def get_queryset(self):
        space_id = self.kwargs.get("space_pk")
        logger.info(f' Get all users from space with id: {space_id}')
        space = get_object_or_404(Space, id=space_id, members=self.request.user)
        logger.info(f' Retrieving all users for space with id: {space_id} and name: {space.name}')
        return space.members.all()

# GET
class CalendarAPIView(generics.ListAPIView):
    """
    Retrieves a list of all habits with their checkmarks for all users in a specific space.
    If the requesting user does not belong to the space a 404 status is returned.
    """
    serializer_class = RecurrentHabitSerializerToRead
    pagination_class = SpaceHabitsPagination

    def get_queryset(self):
        space_id = self.kwargs.get('pk')
        logger.info(f'Get all recurrent habits from space with id: {space_id}')
        space = get_object_or_404(Space, id=space_id, members=self.request.user)
        return space.space_habits.select_subclasses()

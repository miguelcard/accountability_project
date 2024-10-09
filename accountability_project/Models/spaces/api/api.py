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
        user_is_related_to_space = False
        try:
            # query if user is member
            space_role = SpaceRole.objects.get(space__id=space.id, member=user.id)
        except SpaceRole.DoesNotExist:
            space_role = None
        
        if space_role is not None:
            user_is_related_to_space = True
            space_role.delete()
            logger.info(f'space role deleted for user with id: {user.id} uname: {user.username} and space with id: {space.id} name: {space.name}')
            self.unlink_habits(space, user)
            
        # if user is creator additionally replace him by next user in the group,  if no more users are in the group, delete whole space
        if space.creator == self.request.user:
            user_is_related_to_space = True
            logger.info(f'Changing user with id: {user.id} uname: {user.username} from being the creator of space with id: {space.id} name: {space.name}')
            members_list = space.members.all()
            for member in members_list:
                if member is not user:
                    space.creator = member
                    logger.info(f'New creator user with id: {user.id} uname: {user.username} set to space with id: {space.id} name: {space.name}')
                    break

            space.save()
            self.unlink_habits(space, user)

        if not user_is_related_to_space:
            raise NotFound('User does not belong to the Space')

        if not space.members.all():
            space.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def unlink_habits(self, space, user):

        user_habits = user.habits.all()
        space_habits = space.space_habits.all()

        intersection_habits = list(set(user_habits).intersection(space_habits))

        for habit in intersection_habits:
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

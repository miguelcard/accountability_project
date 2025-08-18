import logging
from django.db import models
from django.db.models import fields
from rest_framework import serializers
from Models.spaces.models import Space, SpaceRole
from Models.habits.api.serializers import HabitTagSerializer
from Models.habits.models import BaseHabit, RecurrentHabit
from Models.habits.api.serializers import GoalSerializerToRead, RecurrentHabitSerializerToRead
from Models.users.models import User
import re

logger = logging.getLogger(__name__)

class SimpleUserSerializer(serializers.ModelSerializer):
    """
    Serializer to retrieve general information about the users belonging to the space, which other users can also see 
    """
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "name",
            "avatar_seed",
            "email",
            "about",
            "is_active"
        )
        read_only_fields = (
            "id",
            "username",
            "name",
            "avatar_seed",
            "email",
            "about",
            "is_active"
        )
        
        
class SpaceSerializer(serializers.ModelSerializer):
    
    space_habits = serializers.PrimaryKeyRelatedField(queryset=BaseHabit.objects.all(), many=True, allow_null=True, required=False)

    class Meta:
        model = Space
        fields = '__all__'
        read_only_fields = (
            'creator',
            # members?
        )
    
    def to_representation(self, instance):
        serializer = SpaceSerializerToRead(instance, context=self.context)
        return serializer.data

class SpaceSerializerToRead(serializers.ModelSerializer):
    tags = HabitTagSerializer(many=True, read_only=True)
    members_count = serializers.IntegerField(read_only=True)
    habits_count = serializers.IntegerField(read_only=True)
    space_habits = serializers.PrimaryKeyRelatedField(read_only=True, many=True) # possibly create a nested serializer for this one
    creator = SimpleUserSerializer(read_only=True)
    
    class Meta:
        model = Space
        fields = '__all__'

class SpaceSerializerToReadWithHabitsAndMembers(serializers.ModelSerializer):
    tags = HabitTagSerializer(many=True, read_only=True)
    members_count = serializers.IntegerField(read_only=True)
    habits_count = serializers.IntegerField(read_only=True)
    members = SimpleUserSerializer(many=True, read_only=True)
    # shows the detailed habits that belong to this space
    space_habits = serializers.SerializerMethodField(method_name='get_space_habits')

    class Meta:
        model = Space
        fields = '__all__'
        read_only_fields = (
            'creator',
            'space_habits'
        )
    
    def get_space_habits(self, obj):
        habits = obj.space_habits.all().select_subclasses() 
        response_data = []
        for habit in habits:
            if habit.type == 'recurrent':
                specific_serializer = RecurrentHabitSerializerToRead(habit, context=self.context)
            else:
                specific_serializer = GoalSerializerToRead(habit, context=self.context)
            response_data.append(specific_serializer.data) 
        
        return response_data

class SpaceRoleSerializer(serializers.ModelSerializer):
    """
    When the client (frontend) adds a user to a space, it is easier for it to send the users username or email instead of its PK,
    which is what the SpaceRole would accept. This serializer takes care of that.
    """
    username_email = serializers.CharField(write_only=True, help_text=("username or email of the user to be added to the space"))
    
    class Meta:
        model = SpaceRole
        fields = ['username_email', 'role', 'space']
    
    def create(self, validated_data):
        user = self.extract_user_from_username_or_email(validated_data)
        self.check_number_of_spaces_where_user_belongs_orelse_thow_validation_error(user)

        space_role = SpaceRole.objects.create(member=user, **validated_data)  # Create SpaceRole with user instance
        return space_role
    
    def check_number_of_spaces_where_user_belongs_orelse_thow_validation_error(self, user):
        if user and user.spaceroles.count() >= SpaceRole.MAX_BELONGED_SPACES_PER_USER:
            logger.info(f'SpaceRole Serializer error: User may not be able to belong to more than "{SpaceRole.MAX_BELONGED_SPACES_PER_USER}" spaces, validation error is thrown')
            raise serializers.ValidationError({
                'error': f'{user.username} has reached the limit of belonging to a maximum of '
                          f'{SpaceRole.MAX_BELONGED_SPACES_PER_USER} spaces on the free tier. Therefore the user can not be added to this space.'
            })
    
    def extract_user_from_username_or_email(self, validated_data):
        username_email = validated_data.pop('username_email')  # Remove username from validated data

        # distinguish if the the string sent is the user's username or email
        email_pattern = r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, username_email):
            user = User.objects.get(email=username_email)   # Get user instance by email
        else:
            user = User.objects.get(username=username_email)  # Get user instance by username
        return user


class SpaceRoleSerializerForEdition(serializers.ModelSerializer):
    """
    With space field read only and member (user) read only -> the only way of adding a new user to the space should be only by creating a new space role
    """
    class Meta:
        model = SpaceRole
        fields = '__all__'
        read_only_fields = (
            'space',
            'member'
        )
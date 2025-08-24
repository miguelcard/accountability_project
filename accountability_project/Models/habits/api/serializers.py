from django.db import IntegrityError, transaction
from Models.habits.models import Goal, RecurrentHabit, HabitTag, BaseHabit, CheckMark, Milestone
from rest_framework import serializers
import datetime
from rest_framework.exceptions import ParseError
from Models.spaces.models import Space

# Filters the Checkmarks or Milestones by Date, by default only the ones in the last 7 days are shown
class FilteredListSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        date_from = self.context['request'].GET.get('cm_from_date', None)
        date_to = self.context['request'].GET.get('cm_to_date', None)

        if isinstance(data, list):
            return super(FilteredListSerializer, self).to_representation(data)
        
        try:    
            if (date_from != None and date_to != None):
                data = data.filter(date__range=[date_from, date_to])
            elif(date_from !=None):
                data = data.filter(date__gt=date_from) 
            elif(date_to != None):
                checkmarks_to_date = datetime.datetime.strptime(date_to, '%Y-%m-%d')
                last_week = checkmarks_to_date - datetime.timedelta(days = 7)
                data = data.filter(date__range=[last_week, date_to])
            else:
                today = datetime.date.today() + datetime.timedelta(days = 1)
                last_week = datetime.date.today() - datetime.timedelta(days = 7)
                data = data.filter(date__range=[last_week, today])
        except Exception as e :
            raise ParseError(detail=('Invalid format of dates (date_to or date_from) given, or an invalid date was given ', str(e)))
        return super(FilteredListSerializer, self).to_representation(data)

class CheckMarkNestedSerializer(serializers.ModelSerializer):
    class Meta:
        list_serializer_class = FilteredListSerializer
        model = CheckMark
        fields = '__all__'

class MilestoneNestedSerializer(serializers.ModelSerializer):
    class Meta:
        list_serializer_class = FilteredListSerializer
        model = Milestone
        fields = '__all__'

class HabitTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitTag
        fields = '__all__'

class RecurrentHabitSerializerToWrite(serializers.ModelSerializer):
    spaces = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Space.objects.all(),  # Add queryset for validation
        required=False,
    )
    class Meta:
        model = RecurrentHabit
        fields = '__all__'
        read_only_fields = (
            "owner",
        )
    
    # Method that catches the DB uniqueness/constraint failure (an IntegrityError) and handles it gracefully for the client
    # This ensures that for now one habit can only belong to one space, while still having a join table between them. 
    # It wraps the  creation + join table modifications in transaction.atomic() so a failed add() rolls back the created habit.
    def create(self, validated_data):
        spaces = validated_data.pop('spaces', [])
        # all inside runs in a DB transaction
        try:
            with transaction.atomic():
                habit = RecurrentHabit.objects.create(**validated_data) # creates habit row inside transaction
                if spaces:
                    try:
                        habit.spaces.add(*spaces)  # attempts to create rows in the M2M join table. If the DB unique constraint is violated, the DB raises IntegrityError.
                    except IntegrityError:
                        raise ParseError("Each habit can be assigned to at most one space.")
            return habit
        except ParseError:
            # re-raise so DRF handles it as a 400
            raise
        except Exception as exc:
            # Optional: be conservative and convert unexpected DB integrity issues to a generic ValidationError
            raise ParseError("Could not create habit.")


    # comented for now, would only be needed if user could update a habit and change its space, and even if he could the DB constraint would throw an error.
    # Same funcitonality as in the create method to allow only one space per habit, but in case client updates the habit
    # the instance refers to the model instance, so this method would copy all the other attributes besided the spaces to the model instance
    # and then would check the spaces constraint to either save a unique per habit or throw an error.
    # def update(self, instance, validated_data):
    #     spaces = validated_data.pop('spaces', None)

    #     # copies all other attributes to model instance
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)

    #     try:
    #         with transaction.atomic():
    #             instance.save()
    #             if spaces is not None:
    #                 try:
    #                     instance.spaces.set(spaces)  # set() may also raise IntegrityError
    #                 except IntegrityError:
    #                     raise ParseError('Each habit can be assigned to at most one space.')
    #         return instance
    #     except ParseError:
    #         # re-raise so DRF handles it as a 400
    #         raise
    #     except Exception as exc:
    #         # Optional: be conservative and convert unexpected DB integrity issues to a generic ValidationError
    #         raise ParseError("Could not update habit.")
    
    # implement similar behavioour in update method??

    def to_representation(self, instance):
        serializer = RecurrentHabitSerializerToRead(instance, context=self.context)
        return serializer.data
    
# Overwrites the Serializer to write to make the fields not required for the PATCH methods
class RecurrentHabitSerializerToPatch(RecurrentHabitSerializerToWrite):
    # Set the fields with required=False by default
    times = serializers.IntegerField(required=False)
    time_frame = serializers.CharField(required=False)
    title = serializers.CharField(required=False)


class RecurrentHabitSerializerToRead(serializers.ModelSerializer):
    tags = HabitTagSerializer(many=True, read_only=True)
    checkmarks = CheckMarkNestedSerializer(many=True, read_only=True)

    class Meta:
        model = RecurrentHabit
        fields = '__all__'
        read_only_fields = (
            "owner",
        )
    
class GoalSerializerToWrite(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = (
            "owner",
        )

    def to_representation(self, instance):
        serializer = GoalSerializerToRead(instance, context=self.context)
        return serializer.data

class GoalSerializerToRead(serializers.ModelSerializer):
    tags = HabitTagSerializer(many=True, read_only=True)
    checkmarks = CheckMarkNestedSerializer(many=True, read_only=True)
    milestones = MilestoneNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = (
            "owner",
        )


from Models.habits.models import Goal, RecurrentHabit, HabitTag, BaseHabit, CheckMark, Milestone
from rest_framework import serializers
import datetime
from rest_framework.exceptions import ParseError

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
    class Meta:
        model = RecurrentHabit
        fields = '__all__'
        read_only_fields = (
            "owner",
        )
    
    def to_representation(self, instance):
        serializer = RecurrentHabitSerializerToRead(instance, context=self.context)
        return serializer.data
    
# comment
class RecurrentHabitSerializerToPatch(RecurrentHabitSerializerToWrite):
    # Set the fields with required=False by default
    times = serializers.IntegerField(required=False)
    time_frame = serializers.CharField(required=False)
    

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


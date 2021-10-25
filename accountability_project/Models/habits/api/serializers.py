from Models.habits.models import Goal, RecurrentHabit, HabitTag, BaseHabit, CheckMark
from rest_framework import serializers
import datetime

# Filters the Checkmarks by Date, by default only the ones in the last 7 days are shown
class FilteredListSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        checkmarks_from = self.context['request'].GET.get('checkmarks_from', None)
        checkmarks_to = self.context['request'].GET.get('checkmarks_to', None)

        if isinstance(data, list):
            return super(FilteredListSerializer, self).to_representation(data)
        
        if (checkmarks_from != None and checkmarks_to != None):
            data = data.filter(date__range=[checkmarks_from, checkmarks_to])
        elif(checkmarks_from !=None):
            data = data.filter(date__gt=checkmarks_from) 
        elif(checkmarks_to != None):
            checkmarks_to_date = datetime.datetime.strptime(checkmarks_to, '%Y-%m-%d')
            last_week = checkmarks_to_date - datetime.timedelta(days = 7)
            data = data.filter(date__range=[last_week, checkmarks_to])
        else:
            today = datetime.date.today() + datetime.timedelta(days = 1)
            last_week = datetime.date.today() - datetime.timedelta(days = 7)
            data = data.filter(date__range=[last_week, today])

        return super(FilteredListSerializer, self).to_representation(data)

class CheckMarkNestedSerializer(serializers.ModelSerializer):
    class Meta:
        list_serializer_class = FilteredListSerializer
        model = CheckMark
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
        serializer = RecurrentHabitSerializerToRead(instance)
        return serializer.data

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
        serializer = GoalSerializerToRead(instance)
        return serializer.data


class GoalSerializerToRead(serializers.ModelSerializer):
    tags = HabitTagSerializer(many=True, read_only=True)
    checkmarks = CheckMarkNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = (
            "owner",
        )


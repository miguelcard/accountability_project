from re import S
from django.db import models
from django.db.models import fields
from Models.habits.models import Goal, RecurrentHabit, HabitTag, BaseHabit, CheckMark
from rest_framework import serializers
import datetime

# Firstly the serializers used as "Nested Serializers" for the Habits Serializers

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

# Place at the beggining        
# class CheckMarkSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CheckMark
#         fields = '__all__'

# Filters the Checkmarks by Date, by default only the ones in the last 7 days are shown
class FilteredListSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        # if just from parameter sent use it until today
        # if just to parameter sent, use it -7 days
        # if both sent use those ranges
        # else default 7 days ago to today 

        checkmarks_from = self.context['request'].GET.get('checkmarks_from', None)
        checkmarks_to = self.context['request'].GET.get('checkmarks_to', None)
        
        if (checkmarks_from != None and checkmarks_to != None):
            #filter range
            print('BOTH FROM & TO DEFINED')
            pass
        elif(checkmarks_from !=None):
            print('ONLY FROM DEFINED')
            # data = data.filter(date__gt=checkmarks_from) 
        elif(checkmarks_to != None):
            print('ONLY TO DEFINED')
            
            # data = filter from that dats -7 
        else:
            print('NONE DEFINED')
            pass
             # jsut default today -7

        #data = data.filter(date__gt=checkmarks_from) 
        # data = data.filter(date__gt=datetime.date(2021,10,18)) # user=self.context['request'].user, edition__hide=False)
        # These two are the same: 
        # self.get_query_set().filter(user__isnull=False, modelField=x)
        # self.get_query_set().filter(modelField=x).exclude(user__isnull=True) 
        return super(FilteredListSerializer, self).to_representation(data)

class CheckMarkNestedSerializer(serializers.ModelSerializer):

    class Meta:
        list_serializer_class = FilteredListSerializer
        model = CheckMark
        fields = '__all__'

class GoalSerializerToRead(serializers.ModelSerializer):
    tags = HabitTagSerializer(many=True, read_only=True)
    # checkmark_set = CheckMarkSerializer(many=True, read_only=True)
    checkmarks = CheckMarkNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = (
            "owner",
        )


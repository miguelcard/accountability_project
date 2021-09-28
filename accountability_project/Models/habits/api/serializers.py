from accountability_project.Models.habits.models import Goal, RecurrentHabit
from rest_framework import serializers
from Models.habits.models import BaseHabit

#Not needed?
# class BaseHabitSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BaseHabit
#         fields = '__all__'

class RecurrentHabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurrentHabit
        fields = '__all__'

class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = '__all__'

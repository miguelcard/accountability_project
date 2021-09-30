from Models.habits.models import Goal, RecurrentHabit, HabitTag
from rest_framework import serializers

#Not needed?
# class BaseHabitSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BaseHabit
#         fields = '__all__'

class RecurrentHabitSerializerToWrite(serializers.ModelSerializer):
    class Meta:
        model = RecurrentHabit
        fields = '__all__'

class HabitTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitTag
        fields = '__all__'

class RecurrentHabitSerializerToRead(RecurrentHabitSerializerToWrite):
    tags = HabitTagSerializer(many=True, read_only=True)
    

class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitTag
        fields = '__all__'
from Models.habits.models import Goal, RecurrentHabit, HabitTag
from rest_framework import serializers

#Not needed?
# class BaseHabitSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BaseHabit
#         fields = '__all__'
class HabitTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitTag
        fields = '__all__'

class RecurrentHabitSerializer(serializers.ModelSerializer):
    tags = HabitTagSerializer(many=True, read_only=True) # write explicit fields? add in read_only_fields
    class Meta:
        model = RecurrentHabit
        fields = '__all__'
        read_only_fields = (
            "tags",
        )

class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitTag
        fields = '__all__'
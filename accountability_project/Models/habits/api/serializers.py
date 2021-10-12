from Models.habits.models import BaseHabit
from Models.habits.models import Goal, RecurrentHabit, HabitTag
from rest_framework import serializers

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

class HabitTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitTag
        fields = '__all__'

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

class GoalSerializerToRead(serializers.ModelSerializer):
    tags = HabitTagSerializer(many=True, read_only=True)
    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = (
            "owner",
        )

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitTag
        fields = '__all__'

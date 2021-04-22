from rest_framework import serializers
from Models.habits.models import Habit, StartDay, FinishDay


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = '__all__'


class StartDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = StartDay
        fields = '__all__'


class FinishDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = FinishDay
        fields = '__all__'

from rest_framework import serializers
from Models.habits.models import BaseHabit


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseHabit
        fields = '__all__'

from rest_framework import serializers
from Models.scoreboards.models import Scoreboard


class ScoreboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scoreboard
        fields = '__all__'
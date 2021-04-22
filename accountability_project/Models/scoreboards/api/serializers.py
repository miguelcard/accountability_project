from rest_framework import serializers
from Models.scoreboards.models import ScoreBoard


class ScoreBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoreBoard
        fields = '__all__'
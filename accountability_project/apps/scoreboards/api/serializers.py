from rest_framework import serializers
from apps.scoreboards.models import ScoreBoard


class ScoreBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoreBoard
        fields = '__all__'
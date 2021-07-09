from rest_framework import serializers
from Models.groups.models import Group, Post


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    """class that serialize all attributes of the post model table"""
    class Meta:
        model =  Post
        fields = '__all__'
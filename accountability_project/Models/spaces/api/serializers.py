from django.db import models
from django.db.models import fields
from rest_framework import serializers
from Models.spaces.models import Space, SpaceRole
from Models.habits.api.serializers import HabitTagSerializer

class SpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Space
        fields = '__all__'
        read_only_fields = (
            'creator',
            # members?
        )
    
    def to_representation(self, instance):
        serializer = SpaceSerializerToRead(instance, context=self.context)
        return serializer.data

class SpaceSerializerToRead(serializers.ModelSerializer):
    tags = HabitTagSerializer(many=True, read_only=True)
    # members size
    size = serializers.IntegerField(read_only=True)
    # size = serializers.SerializerMethodField(method_name='get_size')
    
    class Meta:
        model = Space
        fields = '__all__'
        read_only_fields = (
            'creator',
            # 'size',
        )
        
    # def get_size(self, instance):
    #     member_size = instance.members.count()
    #     return member_size

class SpaceRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpaceRole
        fields = '__all__'
        # to create and apply custom permissions on object level, must be done in serializer_class
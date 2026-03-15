from rest_framework import serializers
from Models.users.models import User, Tag, Language
from datetime import date


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'

class UserGetAgeSerializer():
    def get_age(self, obj):
        today = date.today()
        born = obj.birthdate
        if born is None:
            return None
        rest = 1 if (today.month, today.day) < (born.month, born.day) else 0
        return today.year - born.year - rest
  
class UserSerializer(serializers.ModelSerializer, UserGetAgeSerializer):
    age = serializers.SerializerMethodField(method_name='get_age')
    tags = TagSerializer(many=True, read_only=True)
    languages = LanguageSerializer(many=True, read_only=True)
    class Meta:
        model = User
        fields = (
            "id",
            "firebase_uid",
            "is_anonymous_firebase_user",
            "username",
            "name",
            "email",
            "avatar_seed",
            "birthdate",
            "age",
            "gender",
            "tags",
            "languages",
            "about",
            "is_active", 
            "is_superuser",
            "is_staff",
            "created_at",
            "updated_at"
        )
        read_only_fields = (
            "firebase_uid",
            "is_anonymous_firebase_user",
            "tags",
            "languages",
        )


class GetAuthenticatedUserSerializer(serializers.ModelSerializer, UserGetAgeSerializer):
    tags = TagSerializer(many=True, read_only=True)
    languages = LanguageSerializer(many=True, read_only=True)
    age = serializers.SerializerMethodField(method_name='get_age')
    user_spaces = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    owned_spaces = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    
    class Meta:
        model = User
        exclude = ("password",) 
        read_only_fields = (
            "age",
        )
        
        
class UsernameAndEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')
        
        
class CheckEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)

class CheckUsernameSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
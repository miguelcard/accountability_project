from rest_framework import serializers
from Models.users.models import User, Tag, Language
from datetime import date

class RegisterSerializer(serializers.ModelSerializer):
    #This password2 doesnt exist in the model itself but it has to be passed at registration, thats why we create it manually
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password', 'password2'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User(email=self.validated_data['email'], username=self.validated_data['username'])
        password = validated_data['password']
        password2 =validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match'})
        
        user.set_password(password) 
        user.save()
        return user

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'

class UserGetAgeSerializer():
    def get_age(self, instance):
        today = date.today()
        born = instance.birthdate
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
            "username",
            "name",
            "last_name",
            "email",
            "password", 
            "profile_photo",
            "birthdate",
            "age",
            "gender",
            "tags",
            "languages",
            "about",
            "is_active", 
            "is_superuser"
        )
        read_only_fields = (
            "tags",
            "languages"
            # is_active ?
            # is_superuser ?
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        update_user = super().update(instance, validated_data)
        update_user.set_password(validated_data['password'])
        update_user.save()
        return update_user

class UserUpdatedFieldsWithoutPasswordUsernameEmailSerializer(serializers.ModelSerializer, UserGetAgeSerializer):

    age = serializers.SerializerMethodField(method_name='get_age')
    
    class Meta:
        model = User
        exclude = ("password", "username","email", "is_active","is_staff" , "is_superuser",) 
        read_only_fields = (
            "age",
        )

class GetAuthenticatedUserSerializer(UserUpdatedFieldsWithoutPasswordUsernameEmailSerializer):
    tags = TagSerializer(many=True, read_only=True)
    languages = LanguageSerializer(many=True, read_only=True)
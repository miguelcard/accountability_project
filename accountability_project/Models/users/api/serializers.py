from rest_framework import serializers
from Models.users.models import User, Tag, Language

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

class UserSerializer(serializers.ModelSerializer):
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
            "gender",
            "age",
            "tags",
            "languages",
            "about",
            "is_active", 
            "is_superuser"
        )
        read_only_fields = (
            "age",
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

class UserUpdatedFieldsWithoutPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("password", "is_staff",)
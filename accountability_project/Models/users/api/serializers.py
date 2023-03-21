from rest_framework import serializers
from Models.users.models import User, Tag, Language
from datetime import date
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.ModelSerializer):
    #This password2 doesnt exist in the model itself but it has to be passed at registration, thats why we create it manually
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'name', 'username', 'email', 'password', 'password2'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    # def validate(self, attrs):
    #     # here you can add the custpm validations like if the usersemail or username already exist and so on. see: https://www.youtube.com/watch?v=6d0fiPj0dsA 6:00
    #     # or would this validation go on UserSerializer ?
    #     pass

    def create(self, validated_data):
        user = User(email=self.validated_data['email'], username=self.validated_data['username'], name=self.validated_data['name'])
        password = validated_data['password']
        password2 =validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match'})
        
        user.set_password(password) 
        user.save()
        return user


class LoginSerializer(serializers.Serializer):

    email = serializers.CharField(
        label= ("Email"),
        write_only=True
    )
    password = serializers.CharField(
        label= ("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label= ("Token"),
        read_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        print('email: ', email, ' password: ', password)

        if not email or not password:
            msg = ('Please provide both email and password')
            raise serializers.ValidationError(msg, code='authorization')

        if not User.objects.filter(email=email).exists():
            msg = ('Email does not exist.')
            raise serializers.ValidationError(msg, code='authorization')
        
        user = authenticate(request=self.context.get('request'),
                                email=email, password=password)
        if not user:
            msg = ('Wrong credentials')
            raise serializers.ValidationError(msg, code='authorization')
        
        attrs['user'] = user
        return attrs

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
            "is_superuser",
            "is_staff",
            "created_at",
            "updated_at"
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


class UserUpdatedFieldsWithoutPasswordSerializer(serializers.ModelSerializer, UserGetAgeSerializer):

    age = serializers.SerializerMethodField(method_name='get_age')
    
    class Meta:
        model = User
        exclude = ('password',) 
        read_only_fields = (
            'age',
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
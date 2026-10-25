import re

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from Models.users.models import User, Tag, Language
from datetime import date

USERNAME_PATTERN = re.compile(r'[a-z0-9_-]{3,20}')
RESERVED_USERNAME_PREFIX = 'fb_'


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
  
def case_insensitive_username_validators():
    return [UniqueValidator(
        queryset=User.objects.all(),
        lookup='iexact',
        message='A user with that username already exists.',
    )]


class UsernameRulesMixin:
    """
    Usernames are case-insensitive and stored lowercase (see User.save), restricted to
    lowercase ASCII letters, digits, '-' and '_' (3-20 chars), and may not use the 'fb_' prefix
    reserved for placeholder usernames of auto-created Firebase users.
    """

    def validate_username(self, value):
        if value is None:
            return value

        value = value.strip().lower()

        # Leave an unchanged username alone so legacy/placeholder users can still edit other fields.
        if self.instance is not None and value == self.instance.username:
            return value

        if not USERNAME_PATTERN.fullmatch(value):
            raise serializers.ValidationError(
                'Username must be 3-20 characters long and only contain letters, numbers, dashes and underscores.'
            )
        if value.startswith(RESERVED_USERNAME_PREFIX):
            raise serializers.ValidationError(f'Username cannot start with "{RESERVED_USERNAME_PREFIX}".')
        return value


class UserSerializer(UsernameRulesMixin, serializers.ModelSerializer, UserGetAgeSerializer):
    age = serializers.SerializerMethodField(method_name='get_age')
    tags = TagSerializer(many=True, read_only=True)
    languages = LanguageSerializer(many=True, read_only=True)
    class Meta:
        model = User
        extra_kwargs = {'username': {'validators': case_insensitive_username_validators()}}
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


class GetAuthenticatedUserSerializer(UsernameRulesMixin, serializers.ModelSerializer, UserGetAgeSerializer):
    tags = TagSerializer(many=True, read_only=True)
    languages = LanguageSerializer(many=True, read_only=True)
    age = serializers.SerializerMethodField(method_name='get_age')
    user_spaces = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    owned_spaces = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    
    class Meta:
        model = User
        exclude = ("password",) 
        extra_kwargs = {'username': {'validators': case_insensitive_username_validators()}}
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


# ── XP Stats ─────────────────────────────────────────────────────────────────

class XPHeatmapEntrySerializer(serializers.Serializer):
    """One cell of the heatmap — week/month start date and total XP earned."""
    period_start = serializers.DateField()
    xp           = serializers.IntegerField()


class XPStatsSerializer(serializers.Serializer):
    """Full XP stats payload returned by GET /api/v1/user/xp-stats/"""
    total_xp              = serializers.IntegerField()
    level                 = serializers.IntegerField()
    xp_into_level         = serializers.IntegerField(help_text='XP accumulated since reaching current level')
    xp_for_level          = serializers.IntegerField(help_text='XP gap required to advance to next level')
    pct_to_next           = serializers.FloatField(help_text='Progress 0.0–1.0')
    longest_streak        = serializers.IntegerField(help_text='Longest single-habit streak ever (in periods)')
    longest_streak_unit   = serializers.CharField(help_text="Timeframe unit of the longest streak: 'W' (weekly) or 'M' (monthly)")
    completed_periods     = serializers.IntegerField(help_text='Total number of periods where at least one habit was completed')
    heatmap               = XPHeatmapEntrySerializer(many=True)


class PublicUserXPStatsSerializer(serializers.Serializer):
    """Public XP stats payload returned by GET /api/v1/users/{id}/public-stats/"""
    level                 = serializers.IntegerField()
    total_xp              = serializers.IntegerField()
    xp_into_level         = serializers.IntegerField(help_text='XP accumulated since reaching current level')
    xp_for_level          = serializers.IntegerField(help_text='XP gap required to advance to next level')
    pct_to_next           = serializers.FloatField(help_text='Progress 0.0–1.0')
    longest_streak        = serializers.IntegerField(help_text='Longest single-habit streak ever (in periods)')
    longest_streak_unit   = serializers.CharField(help_text="Timeframe unit of the longest streak: 'W' (weekly) or 'M' (monthly)")
    completed_periods     = serializers.IntegerField(help_text='Total number of periods where at least one habit was completed')
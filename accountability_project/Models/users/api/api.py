import logging
import time

from django.http import request
from firebase_admin import auth as firebase_auth
from firebase_admin.exceptions import FirebaseError
from Models.spaces.api.api import SpaceRoleCleanupMixin
from Models.spaces.models import PendingInvite, SpaceRole
from rest_framework.permissions import IsAdminUser
from Models.users.models import User, Tag, Language
from Models.users.api.serializers import CheckEmailSerializer, CheckUsernameSerializer, UserSerializer, GetAuthenticatedUserSerializer, LanguageSerializer, TagSerializer, UsernameAndEmailSerializer, XPStatsSerializer, PublicUserXPStatsSerializer
from rest_framework import status, generics, mixins 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from Models.users.api.pagination import GenericUserPagination
from django.db.models import Q, Sum
from django.db import models as django_models
from django.db import IntegrityError, transaction
from rest_framework import permissions
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)

# How recent the Firebase sign-in must be to allow deleting a registered account.
ACCOUNT_DELETE_MAX_AUTH_AGE_SECONDS = 5 * 60

class LoggedInUserApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        """
        Permanently deletes the authenticated user's account.

        - Registered (non-anonymous) users must have signed in recently (Firebase `auth_time`),
          so a stolen/idle session cannot wipe an account. The frontend re-authenticates first.
        - The user leaves every space as if they left it manually (admin promotion, creator
          transfer, empty-space removal, their habits in those spaces are deleted).
        - The Firebase user is deleted last, inside the DB transaction: if Firebase fails,
          everything is rolled back so the user can simply retry.
        """
        user = request.user

        if not user.is_anonymous_firebase_user and not self._signed_in_recently(request):
            return Response(
                {
                    'detail': 'Please sign in again to confirm deleting your account.',
                    'code': 'recent_login_required',
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        firebase_uid = user.firebase_uid
        email = user.email
        user_id = user.id
        try:
            with transaction.atomic():
                self._leave_all_spaces(user)
                PendingInvite.objects.filter(email__iexact=email, accepted=False).delete()
                user.delete()
                if firebase_uid:
                    self._delete_firebase_user(firebase_uid)
        except FirebaseError:
            logger.exception('Could not delete Firebase user for django user id=%s; rolled back', user_id)
            return Response(
                {'detail': 'We could not delete your account right now. Please try again later.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        logger.info('Deleted account of user id=%s', user_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _signed_in_recently(request) -> bool:
        auth_time = (request.auth or {}).get('auth_time') if isinstance(request.auth, dict) else None
        if not isinstance(auth_time, (int, float)):
            return False
        return time.time() - auth_time <= ACCOUNT_DELETE_MAX_AUTH_AGE_SECONDS

    @staticmethod
    def _leave_all_spaces(user):
        cleanup = SpaceRoleCleanupMixin()
        for space_role in list(SpaceRole.objects.filter(member=user).select_related('space')):
            cleanup.cleanup_space_role(space_role, delete_habits=True)

    @staticmethod
    def _delete_firebase_user(firebase_uid):
        try:
            firebase_auth.delete_user(firebase_uid)
        except firebase_auth.UserNotFoundError:
            # Already gone from Firebase, which is the state we want.
            logger.warning('Firebase user %s was already deleted', firebase_uid)

    def get_serializer_class(self):
        if self.request is not None and self.request.method == 'PUT':
            return UserSerializer
        return GetAuthenticatedUserSerializer

    def perform_update(self, serializer):
        # The serializer validators catch duplicates up front, but two simultaneous requests can both
        # pass them; the DB constraints then decide, and the loser should get a 400 rather than a 500.
        try:
            with transaction.atomic():
                serializer.save()
        except IntegrityError:
            field = 'username' if 'username' in serializer.validated_data else 'email'
            raise ValidationError({field: [f'A user with that {field} already exists.']})

class GetAllUserTagsApiView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class GetAllUserLanguagesApiView(generics.ListAPIView):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer

# This API is available to Admins only to perform operations on Users
class UsersAdminApiView(generics.GenericAPIView,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin
                        ):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, pk=None):
        if pk:
            return self.retrieve(request, pk)
        else:
            return self.list(request)
         

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return UserSerializer
        return UserSerializer 
    
# This API is available to Admins only to perform operations on a single User
class SingleUserAdminApiView(UsersAdminApiView, mixins.DestroyModelMixin):
        
        def delete(self, request, pk=None):
            return self.destroy(request, pk)
        
        
class UsernameAndEmailSearchView(generics.ListAPIView):
    """
    Searches and matches the given string, against all the users usernames and emails.
    This endpoint can be accessed by all users as long as they are authenticated.
    """
    serializer_class = UsernameAndEmailSerializer
    pagination_class = GenericUserPagination
    filter_backends = [SearchFilter]
    search_fields = ['username']
    queryset = User.objects.all()
    
    def filter_queryset(self, queryset):
        search_query = self.request.query_params.get('search', '')
        # if the search query parameter is blank or it does not exist, do not show any result
        if not search_query.strip():
            return User.objects.none()
        queryset = super().filter_queryset(queryset)

        # return queryset;
        return sorted(queryset, key=lambda user: (search_query.lower() in user.username.lower()), reverse=True)
    
    
    
class CheckEmailUsernameView(generics.RetrieveAPIView):
    """
    Checks if either the email or username sent in the request paramterers already exist or not, returns { email_taken: true } or { username_taken: true } 
    if the email/username exist, false otherwise.
    """
    
    permission_classes = (permissions.AllowAny,)

    
    def retrieve(self, request, *args, **kwargs):
        email_serializer = CheckEmailSerializer(data=request.query_params)
        email_serializer.is_valid()

        username_serializer = CheckUsernameSerializer(data=request.query_params)
        username_serializer.is_valid()

        email = email_serializer.validated_data.get('email')
        username = username_serializer.validated_data.get('username')

        user_with_email = User.objects.filter(email__iexact=email).exists() if email else False
        user_with_username = User.objects.filter(username=username.strip().lower()).exists() if username else False

        return Response({'email_taken': user_with_email, 'username_taken': user_with_username}, status=status.HTTP_200_OK)


class XPStatsView(generics.GenericAPIView):
    """
    GET /api/v1/user/xp-stats/

    Returns the authenticated user's XP summary:
      - total_xp, level, progress to next level
      - longest streak (in periods) across all habits
      - count of distinct completed periods
      - heatmap data (period_start + XP) for the last 104 periods (~2 years)

    Also reconciles any XP that the signal may have missed (lazy on-demand
    computation — safe to call on every profile load).
    """
    permission_classes = [IsAuthenticated]
    serializer_class   = XPStatsSerializer

    def get(self, request, *args, **kwargs):
        from Models.habits.xp_utils import reconcile_user_xp, level_from_xp
        from Models.habits.models import UserXPLedger

        user = request.user

        # Lazy reconciliation: award any missed XP for closed periods
        reconcile_user_xp(user)

        ledger_qs = UserXPLedger.objects.filter(user=user)

        # Total XP
        total_xp = ledger_qs.aggregate(total=Sum('xp_awarded'))['total'] or 0

        # Level info
        level_info = level_from_xp(total_xp)

        # Longest streak (snapshot stored on each row)
        longest_streak = ledger_qs.aggregate(
            longest=django_models.Max('streak_at_award')
        )['longest'] or 0

        # Unit of the longest streak row ('W' or 'M', derived from reason)
        # MONTHLY_HABIT is preferred on a tie since it represents more real-world time.
        longest_streak_row = (
            ledger_qs
            .filter(streak_at_award=longest_streak)
            .order_by('reason')  # 'MONTHLY_HABIT' < 'WEEKLY_HABIT' alphabetically; ascending puts MONTHLY first
            .values('reason')
            .first()
        )
        if longest_streak_row and longest_streak_row['reason'] == 'MONTHLY_HABIT':
            longest_streak_unit = 'M'
        else:
            longest_streak_unit = 'W'

        # Distinct completed periods
        completed_periods = ledger_qs.values('period_start').distinct().count()

        # Heatmap: XP per period_start, last 104 entries
        heatmap = (
            ledger_qs
            .values('period_start')
            .annotate(xp=Sum('xp_awarded'))
            .order_by('-period_start')[:104]
        )
        heatmap_data = [
            {'period_start': entry['period_start'], 'xp': entry['xp']}
            for entry in heatmap
        ]

        payload = {
            'total_xp':            total_xp,
            'level':               level_info['level'],
            'xp_into_level':       level_info['xp_into_level'],
            'xp_for_level':        level_info['xp_for_level'],
            'pct_to_next':         level_info['pct_to_next'],
            'longest_streak':      longest_streak,
            'longest_streak_unit': longest_streak_unit,
            'completed_periods':   completed_periods,
            'heatmap':             heatmap_data,
        }

        serializer = self.get_serializer(payload)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PublicUserXPStatsView(generics.GenericAPIView):
    """
    GET /api/v1/users/{id}/public-stats/

    Returns the target user's XP summary (no heatmap). Any authenticated user
    can read any other user's stats — no ownership restriction.
    Returns 404 if the user does not exist.
    """
    permission_classes = [IsAuthenticated]
    serializer_class   = PublicUserXPStatsSerializer

    def get(self, request, pk, *args, **kwargs):
        from Models.habits.xp_utils import level_from_xp
        from Models.habits.models import UserXPLedger
        from django.shortcuts import get_object_or_404

        target_user = get_object_or_404(User, pk=pk)

        ledger_qs = UserXPLedger.objects.filter(user=target_user)

        # Total XP
        total_xp = ledger_qs.aggregate(total=Sum('xp_awarded'))['total'] or 0

        # Level info
        level_info = level_from_xp(total_xp)

        # Longest streak (snapshot stored on each row)
        longest_streak = ledger_qs.aggregate(
            longest=django_models.Max('streak_at_award')
        )['longest'] or 0

        # Unit of the longest streak row ('W' or 'M', derived from reason)
        # MONTHLY_HABIT is preferred on a tie since it represents more real-world time.
        longest_streak_row = (
            ledger_qs
            .filter(streak_at_award=longest_streak)
            .order_by('reason')  # 'MONTHLY_HABIT' < 'WEEKLY_HABIT' alphabetically
            .values('reason')
            .first()
        )
        if longest_streak_row and longest_streak_row['reason'] == 'MONTHLY_HABIT':
            longest_streak_unit = 'M'
        else:
            longest_streak_unit = 'W'

        # Distinct completed periods
        completed_periods = ledger_qs.values('period_start').distinct().count()

        payload = {
            'level':               level_info['level'],
            'total_xp':            total_xp,
            'xp_into_level':       level_info['xp_into_level'],
            'xp_for_level':        level_info['xp_for_level'],
            'pct_to_next':         level_info['pct_to_next'],
            'longest_streak':      longest_streak,
            'longest_streak_unit': longest_streak_unit,
            'completed_periods':   completed_periods,
        }

        serializer = self.get_serializer(payload)
        return Response(serializer.data, status=status.HTTP_200_OK)
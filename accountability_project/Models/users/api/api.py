from django.http import request
from rest_framework.permissions import IsAdminUser
from Models.users.models import User, Tag, Language
from Models.users.api.serializers import CheckEmailSerializer, CheckUsernameSerializer, UserSerializer, GetAuthenticatedUserSerializer, LanguageSerializer, TagSerializer, UsernameAndEmailSerializer, XPStatsSerializer
from rest_framework import status, generics, mixins 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from Models.users.api.pagination import GenericUserPagination
from django.db.models import Q, Sum
from django.db import models as django_models
from rest_framework import permissions

class LoggedInUserApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if self.request is not None and self.request.method == 'PUT':
            return UserSerializer
        return GetAuthenticatedUserSerializer

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

        user_with_email = User.objects.filter(email=email.lower()).exists() if email else False
        user_with_username = User.objects.filter(username=username.lower()).exists() if username else False

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
            'total_xp':          total_xp,
            'level':             level_info['level'],
            'xp_into_level':     level_info['xp_into_level'],
            'xp_for_level':      level_info['xp_for_level'],
            'pct_to_next':       level_info['pct_to_next'],
            'longest_streak':    longest_streak,
            'completed_periods': completed_periods,
            'heatmap':           heatmap_data,
        }

        serializer = self.get_serializer(payload)
        return Response(serializer.data, status=status.HTTP_200_OK)
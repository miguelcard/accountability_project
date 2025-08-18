from django.http import request
from rest_framework.permissions import IsAdminUser
from Models.users.models import User, Tag, Language
from Models.users.api.serializers import CheckEmailSerializer, CheckUsernameSerializer, UserSerializer, UserUpdatedFieldsWithoutPasswordSerializer, GetAuthenticatedUserSerializer, LanguageSerializer, TagSerializer, UsernameAndEmailSerializer
from rest_framework import status, generics, mixins 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from Models.users.api.pagination import GenericUserPagination
from django.db.models import Q
from rest_framework import permissions

class LoggedInUserApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserUpdatedFieldsWithoutPasswordSerializer 

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if(self.request is not None and self.request.method == 'PUT'):
            return UserUpdatedFieldsWithoutPasswordSerializer
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
        print("request: ", self.request)
        if(self.request.method == 'PUT'):
            return UserUpdatedFieldsWithoutPasswordSerializer
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
    # search_fields = ['username', 'email']
    search_fields = ['username']
    queryset = User.objects.all()
    
    def filter_queryset(self, queryset):
        search_query = self.request.query_params.get('search', '')
        if not search_query.strip():
            return User.objects.none()
        queryset = super().filter_queryset(queryset)

        # return queryset;
        return sorted(queryset, key=lambda user: (search_query.lower() in user.username.lower()), reverse=True)
    
        from django.db.models import Case, When, IntegerField, Value
        queryset = queryset.annotate(
            rank=Case(
                When(username__istartswith=search_query, then=Value(2)),
                When(username__icontains=search_query, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by('-rank', 'username')

        return queryset

    
    # if the search query parameter is blank or it does not exist, do not show any result
    # def filter_queryset(self, queryset):
    #     search_query = self.request.query_params.get('search', None)
        
    #     if search_query is None or search_query.strip() == '':
    #         return User.objects.none()

    #     queryset = super().filter_queryset(queryset)

    #     # Create a Q object to filter based on username or email
    #     username_q = Q(username__icontains=search_query)
    #     email_q = Q(email__icontains=search_query)

    #     # Apply the Q object to filter the queryset
    #     queryset = queryset.filter(username_q | email_q)

    #     # Sort the queryset based on whether the username or email contains the search parameter
    #     queryset = sorted(queryset, key=lambda user: (search_query.lower() in user.username.lower(), search_query.lower() in user.email.lower()), reverse=True)
        
    #     return queryset
    
    
    
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
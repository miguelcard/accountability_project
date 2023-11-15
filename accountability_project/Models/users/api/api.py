from django.http import request
from rest_framework.permissions import IsAdminUser
from Models.users.models import User, Tag, Language
from Models.users.api.serializers import UserSerializer, UserUpdatedFieldsWithoutPasswordSerializer, GetAuthenticatedUserSerializer, LanguageSerializer, TagSerializer
from rest_framework import status, generics, mixins 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

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
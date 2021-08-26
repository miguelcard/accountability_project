from django.http import request
from rest_framework.permissions import IsAdminUser
from Models.users.models import User, Tag, Language
from Models.users.api.serializers import UserSerializer, UserUpdatedFieldsWithoutPasswordUsernameEmailSerializer, GetAuthenticatedUserSerializer, LanguageSerializer, TagSerializer
from rest_framework import status, generics, mixins 
from rest_framework.response import Response

class LoggedInUserApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserUpdatedFieldsWithoutPasswordUsernameEmailSerializer 

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if(self.request.method == 'PUT'):
            return UserUpdatedFieldsWithoutPasswordUsernameEmailSerializer
        return GetAuthenticatedUserSerializer

class GetAllUserTagsApiView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class GetAllUserLanguagesApiView(generics.ListAPIView):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer

# This API is available to Admins only 
class UserGenericApiView(generics.GenericAPIView,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.DestroyModelMixin
                        ):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get(self, request, pk=None):
        if pk:
            return self.retrieve(request, pk)
        else:
            return self.list(request)

    def delete(self, request, pk=None):
        return self.destroy(request, pk)   

    def get_serializer_class(self):
        if(request.method == 'PUT'):
            return UserUpdatedFieldsWithoutPasswordUsernameEmailSerializer
        return UserSerializer 

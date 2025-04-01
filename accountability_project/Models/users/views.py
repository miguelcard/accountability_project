from Models.users.api.serializers import UserSerializer
from rest_framework.response import Response
from Models.users.api.serializers import RegisterSerializer, UserSerializer
from django.contrib.auth import login
from rest_framework import generics
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from rest_framework import permissions
from rest_framework.authtoken.serializers import AuthTokenSerializer
from Models.users.api.serializers import LoginSerializer
from rest_framework import status
from knox import views as knox_views
from Models.users.auth_utils import TokenAuthSupportCookie


# Register API
class RegisterAPI(generics.GenericAPIView): # any advantage when using KnoxRegisterView instead?
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        response = Response({"user": UserSerializer(user, context=self.get_serializer_context()).data})
        token = AuthToken.objects.create(user)[1]

        return set_auth_cookie(response, token)

#Login API 
class LoginAPI(KnoxLoginView):
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            login(request, user)
        else:
            return Response({'errors' : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        response = super(LoginAPI, self).post(request, format=None)
        token = response.data['token']
        del response.data['token']

        return set_auth_cookie(response, token)


# Sets the cookie to the response object and returns it
def set_auth_cookie(response, token):
    response.set_cookie(
            'auth_token',
            token,
            httponly=True,
            samesite='strict'
        )

    return response


class CustomLogoutView(knox_views.LogoutView):
    authentication_classes = (TokenAuthSupportCookie,)
    

class CustomLogoutAllView(knox_views.LogoutAllView):
    authentication_classes = (TokenAuthSupportCookie,)
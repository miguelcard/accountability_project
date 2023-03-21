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

# Register API
class RegisterAPI(generics.GenericAPIView): # any advantage when using KnoxRegisterView instead?
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
        "user": UserSerializer(user, context=self.get_serializer_context()).data,
        "authentication": {"token": AuthToken.objects.create(user)[1]}
        })

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

        return Response({
                "user":UserSerializer(user, context={'request': request}).data,
                "authentication": super(LoginAPI, self).post(request, format=None).data
            })
        


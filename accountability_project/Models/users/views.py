from datetime import datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from Models.users.api.serializers import UserTokenserializer
from django.contrib.sessions.models import Session


class Login(ObtainAuthToken):
    """class that create a token id for the login view rout"""

    def post(self, request, *args, **kwargs):
        """how we received two data that is:
           username and password we need a serialize this data
           we will find this serializer inside of ObtainAuthToken
           that its call serializer_class that contain two things
           first the username variable and second the password variable
        """
        login_serializer = self.serializer_class(
            data=request.data, context={'request': request})
        if login_serializer.is_valid():
            user = login_serializer.validated_data['user']
            if user.is_active:
                token, created = Token.objects.get_or_create(user=user)
                user_serializer = UserTokenserializer(user)
                if created:
                    return Response({
                        'token': token.key,
                        'user': user_serializer.data,
                        'message': 'Success Login'
                    }, status=status.HTTP_201_CREATED)
                else:
                    token.delete()
                    token = Token.objects.create(user=user)
                    return Response({
                        'token': token.key,
                        'user': user_serializer.data,
                        'message': 'Success Login'
                    }, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'this user can\'t login'},
                                status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'message': 'invalid email or password'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'hello'}, status=status.HTTP_200_OK)


class Logout(APIView):

    def post(self, request, *args, **kwargs):
        try:
            token_id = request.POST.get('token')
            token = Token.objects.filter(key=token_id).first()

            if token:
                user = token.user
                all_sessions = Session.objects.filter(expire_date__gte=datetime.now())
                if all_sessions.exists():
                    for session in all_sessions:
                        session_data = session.get_decoded()
                        if user.id == int(session_data.get('_auth_user_id')):
                            session.delete()

                token.delete()
                session_message = 'User Session Delete.'
                token_message = 'token delete.'
                return Response({
                    'token_message': token_message,
                    'session_message': session_message,
                }, status=status.HTTP_200_OK)

            return Response({'Error': 'User Credential  Not Found'},
                            status=status.HTTP_400_BAD_REQUEST)

        except :
            return Response({
                'Error': 'Token Not Found'
            }, status = status.HTTP_409_CONFLICT)
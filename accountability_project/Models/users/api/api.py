from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from Models.users.models import User
from Models.users.api.serializers import UserSerializer


@api_view(['GET', 'POST'])
def user_api_view(request):

    if request.method == 'GET':
        users = User.objects.all()
        users_serializer = UserSerializer(users, many=True)
        return Response(users_serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response(user_serializer.data,
                            status=status.HTTP_200_OK)
        return Response(
            {'message': 'Fields not Allowed, a user already exists with these data'},
            status=status.HTTP_400_BAD_REQUEST)
    return Response({'Message': 'An error occurred when sending the data'},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def user_datail_api_view(request, pk=None):
    user = User.objects.filter(id=pk).first()

    if user:
        if request.method == 'GET':
            user_serializer = UserSerializer(user)
            return Response(user_serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'PUT':
            user_serializer = UserSerializer(user, data=request.data)
            if user_serializer.is_valid():
                user_serializer.save()
                return Response(user_serializer.data, status=status.HTTP_200_OK)
            return Response({'message': 'Fields not Allowed'},
                            status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            user.delete()
            return Response({'Message': 'user has been delete'},
                            status=status.HTTP_200_OK)

    return Response({'Message': 'User not found'},
                    status=status.HTTP_400_BAD_REQUEST)

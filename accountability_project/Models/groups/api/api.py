from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
#from rest_framework.decorators import api_view
from Models.groups.models import Group
from Models.groups.api.serializers import GroupSerializer

class GroupApiView(APIView):

    def get(self, request):
        groups = Group.objects.all()
        groups_serializer = GroupSerializer(groups, many=True)
        return Response(groups_serializer.data, status= status.HTTP_200_OK)

    def post(self, request):
        groups_serializer = GroupSerializer(data = request.data)
        if groups_serializer.is_valid():
            groups_serializer.save()
            return Response(groups_serializer.data, status= status.HTTP_201_CREATED)
        return Response(groups_serializer.errors, status= status.HTTP_400_BAD_REQUEST)

class GroupDetailApiView(APIView):

    # method to just get  group object and check if its valid
    def get_object(self, pk):
        try:
            return Group.objects.get(id = pk)
        except Group.DoesNotExist:
            return Response({'Message':'group not found'}, status= status.HTTP_404_NOT_FOUND)

    def get(self, request, pk):
        group = self.get_object(pk)
        group_serializer = GroupSerializer(group)
        return Response(group_serializer.data, status= status.HTTP_200_OK)

    def put(self, request, pk):
        group = self.get_object(pk)
        group_serializer = GroupSerializer(group, data = request.data)
        if group_serializer.is_valid():
            group_serializer.save()
            return Response(group_serializer.data, status= status.HTTP_200_OK)
        return Response({'message': 'Object fields not allowed'}, status= status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        group = self.get_object(pk)
        group.delete()
        return Response({'Message':'group has been deleted'}, status= status.HTTP_204_NO_CONTENT)



"""
@api_view(['GET', 'POST'])
def group_api_view(request):

    if request.method == 'GET':
        groups = Group.objects.all()
        groups_serializer = GroupSerializer(groups, many=True)
        return Response(groups_serializer.data, status= status.HTTP_200_OK)

    elif request.method == 'POST':
        groups_serializer = GroupSerializer(data = request.data)
        if groups_serializer.is_valid():
            groups_serializer.save()
            return Response(groups_serializer.data, status= status.HTTP_201_CREATED)
        return Response(groups_serializer.errors, status= status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'PUT', 'DELETE'])
def group_detail_api_view(request, pk=None): #pk=None ?
    group = Group.objects.filter(id = pk).first()

    if group:
        if request.method == 'GET':
            group_serializer = GroupSerializer(group)
            return Response(group_serializer.data, status= status.HTTP_200_OK)

        elif request.method == 'PUT':
            group_serializer = GroupSerializer(group, data = request.data)
            if group_serializer.is_valid():
                group_serializer.save()
                return Response(group_serializer.data, status= status.HTTP_200_OK)
            return Response({'message': 'Fields not Allowed'}, status= status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            group.delete()
            return Response({'Message':'group has been deleted'}, status= status.HTTP_200_OK)

    return Response({'Message':'group not found'}, status= status.HTTP_404_NOT_FOUND)
"""
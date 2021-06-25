from rest_framework import request, status
from rest_framework.response import Response
from rest_framework.views import APIView
from Models.groups.models import Group
from Models.groups.api.serializers import GroupSerializer
from rest_framework import generics, mixins

class GroupGenericApiView(generics.GenericAPIView,
                            mixins.ListModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.CreateModelMixin, 
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin
                            ):
    
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def get(self, request, pk=None):
        if pk:
            return self.retrieve(request, pk)
        else:
            return self.list(request)

    def post(self, request):
        return self.create(request)

    def put(self, pk):
        return self.update(request, pk)

    def delete(self, pk):
        return self.destroy(request, pk)

    

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
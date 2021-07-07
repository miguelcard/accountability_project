from Models.users.models import User
from Models.groups.models import Group
from Models.groups.api.serializers import GroupSerializer
from rest_framework import generics, mixins

""" ---------views for groups--------"""

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

    def put(self, request, pk=None):
        return self.update(request, pk)

    def delete(self, request, pk=None):
        return self.destroy(request, pk)


# use perform methods to add custom logic, https://www.django-rest-framework.org/api-guide/generic-views/#mixins
from Models.users.models import User
from Models.users.api.serializers import UserSerializer, UserUpdatedFieldsWithoutPasswordSerializer
from rest_framework import generics, mixins 

class UserGenericApiView(generics.GenericAPIView,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.DestroyModelMixin
                        ):

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, pk=None):
        if pk:
            return self.retrieve(request, pk)
        else:
            return self.list(request)

    def delete(self, request, pk=None):
        return self.destroy(request, pk)

class UpdateUserWithoutPasswordApiView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdatedFieldsWithoutPasswordSerializer
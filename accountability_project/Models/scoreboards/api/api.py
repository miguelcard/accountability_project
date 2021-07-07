from Models.scoreboards.models import Scoreboard
from Models.scoreboards.api.serializers import ScoreboardSerializer
from rest_framework import generics, mixins

""" ---------views for scoreboards--------"""

class ScoreboardGenericApiView(generics.GenericAPIView,
                            mixins.ListModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.CreateModelMixin, 
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin
                            ):
    
    queryset = Scoreboard.objects.all()
    serializer_class = ScoreboardSerializer

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
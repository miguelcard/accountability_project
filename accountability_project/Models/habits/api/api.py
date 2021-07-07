from Models.habits.models import Habit
from Models.habits.api.serializers import HabitSerializer
from rest_framework import generics, mixins

""" ---------views for habits--------"""

class HabitGenericApiView(generics.GenericAPIView,
                            mixins.ListModelMixin, 
                            mixins.RetrieveModelMixin, 
                            mixins.CreateModelMixin,
                            mixins.UpdateModelMixin, 
                            mixins.DestroyModelMixin):

    queryset = Habit.objects.all()
    serializer_class = HabitSerializer

    def get(self, request, pk=None):
        if pk:
            return self.retrieve(request, pk)
        else:
            return self.list(request)

    def post(self, request):
        return self.create(request)

    def put(self, request, pk):
        return self.update(request, pk=None)

    def delete(self, request, pk):
        return self.destroy(request, pk=None)
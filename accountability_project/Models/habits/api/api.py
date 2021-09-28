from django.http import request
from Models.habits.api.serializers import RecurrentHabitSerializer
from Models.users.models import User
from Models.habits.models import BaseHabit
from Models.habits.api.serializers import BaseHabitSerializer
from rest_framework import generics, mixins

""" ---------views for habits--------"""

class RecurrentHabitApiView(generics.RetrieveUpdateDestroyAPIView):
    # queryset = # Only Recurrent habits belonging to current user 
    serializer_class = RecurrentHabitSerializer

    def get_queryset(self):
        return BaseHabit.objects.filter(owner=self.request.user) #TEST!


#  #Maybe not the way 
# class BaseHabitApiView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = User.basehabits.all() ##??
#     serializer_class = BaseHabitSerializer


#     def get_serializer_class(self):
#         # if its requestinga goal or its requesting a recurrent habit.... 
#         return super().get_serializer_class()


# class HabitGenericApiView(generics.GenericAPIView,
#                             mixins.ListModelMixin, 
#                             mixins.RetrieveModelMixin, 
#                             mixins.CreateModelMixin,
#                             mixins.UpdateModelMixin, 
#                             mixins.DestroyModelMixin):

#     queryset = BaseHabit.objects.all()
#     serializer_class = HabitSerializer

#     def get(self, request, pk=None):
#         if pk:
#             return self.retrieve(request, pk)
#         else:
#             return self.list(request)

#     def post(self, request):
#         return self.create(request)

#     def put(self, request, pk):
#         return self.update(request, pk=None)

#     def delete(self, request, pk):
#         return self.destroy(request, pk=None)
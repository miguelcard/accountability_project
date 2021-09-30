from django.http import request
from Models.habits.api.serializers import RecurrentHabitSerializerToRead, RecurrentHabitSerializerToWrite
from Models.habits.models import BaseHabit, RecurrentHabit
# from Models.habits.api.serializers import BaseHabitSerializer
from rest_framework import generics

""" ---------views for habits--------"""

class RecurrentHabitApiView(generics.ListCreateAPIView): 
    serializer_class = RecurrentHabitSerializerToRead

    def get_queryset(self):
        return RecurrentHabit.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if(self.request is not None and self.request.method == 'POST'):
            return RecurrentHabitSerializerToWrite
        return RecurrentHabitSerializerToRead


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
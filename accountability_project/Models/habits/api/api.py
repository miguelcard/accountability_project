from django.http import request
from rest_framework.serializers import Serializer
from Models.habits.api.serializers import RecurrentHabitSerializerToRead, RecurrentHabitSerializerToWrite, GoalSerializerToRead, GoalSerializerToWrite
from Models.habits.models import BaseHabit, RecurrentHabit, Goal
# from Models.habits.api.serializers import BaseHabitSerializer
from rest_framework import generics

""" ---------views for habits--------"""

""" ---------views for recurrent habits-------"""

# GET & POST
class RecurrentHabitApiView(generics.ListCreateAPIView): 
    serializer_class = RecurrentHabitSerializerToRead

    def get_queryset(self):
        return RecurrentHabit.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if(self.request is not None and self.request.method == 'POST'):
            return RecurrentHabitSerializerToWrite
        return RecurrentHabitSerializerToRead
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# PUT, PATCH, DELETE & GET (detailed)
class RecurrentHabitDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RecurrentHabitSerializerToWrite

    def get_queryset(self):
        return RecurrentHabit.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if(self.request is not None and self.request.method == 'GET'):
            return RecurrentHabitSerializerToRead
        return RecurrentHabitSerializerToWrite

""" ---------views for Goals-------"""
# GET & POST
class GoalApiView(generics.ListCreateAPIView): 
    serializer_class = GoalSerializerToRead

    def get_queryset(self):
        return Goal.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if(self.request is not None and self.request.method == 'POST'):
            return GoalSerializerToWrite
        return GoalSerializerToRead
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        
# PUT, PATCH, DELETE & GET (detailed)
class GoalDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GoalSerializerToRead

    def get_queryset(self):
        return Goal.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if(self.request is not None and self.request.method == 'GET'):
            return GoalSerializerToRead
        return GoalSerializerToWrite

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
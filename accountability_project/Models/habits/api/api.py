from django.http import request, response
from rest_framework.serializers import Serializer
from Models.habits.api.serializers import RecurrentHabitSerializerToRead, RecurrentHabitSerializerToWrite, GoalSerializerToRead, GoalSerializerToWrite, BaseHabitSerializer
from Models.habits.models import BaseHabit, RecurrentHabit, Goal
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from itertools import chain

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






class AllHabitsApiView2(generics.ListAPIView): 
    serializer_class = GoalSerializerToRead

    def get_queryset(self):
        return Goal.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if(self.request is not None and self.request.method == 'POST'):
            return GoalSerializerToWrite
        return GoalSerializerToRead
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# GET    MAYBE THE POST DOES NOT MAKE MUCH SENSE WITH THIS ONE 
class AllHabitsApiView(generics.GenericAPIView): 
    #add sorting by: created, updated, type, title, tag(?), space(?)
    filter_backends = [OrderingFilter]
    ordering_fields = ['id', 'title', 'created_at', 'updated_at', 'type', 'start_date', 'finish_date']

    def get(self, request, *args, **kwargs):
        recurrent_habits = RecurrentHabit.objects.filter(owner=self.request.user)
        goals = Goal.objects.filter(owner=self.request.user)
        context = {"request": request,}

        # recurrent_habits = self.filter_queryset(recurrent_habits) #just filters the recurrent habits

        #habits_list = (chain(recurrent_habits, goals))
        #filtered_data = self.filter_queryset(habits_list)

        recurrent_habits_serializer = RecurrentHabitSerializerToRead(recurrent_habits, many=True, context=context)
        goal_serializer = GoalSerializerToRead(goals, many=True, context=context)
        
        # can I sort and combine these 2 before?
        response_data = recurrent_habits_serializer.data + goal_serializer.data

        # All Habits queryset
        all_habits = BaseHabit.objects.filter(owner=self.request.user).select_subclasses()
        filtered_habits = self.filter_queryset(all_habits)
        for habit in filtered_habits:
            print(habit)
        test_serializer = BaseHabitSerializer(filtered_habits, many=True, context=context)
         
        return Response(test_serializer.data)
        return Response(response_data)
        
        

    # #Can I pass both from objects one queryset? if yest I can use ListAPIView
    # def get_queryset(self):
    #     return RecurrentHabit.objects.filter(owner=self.request.user) + Goal.objects.filter(owner=self.request.user)

    # def get_serializer_class(self):
    #     if(self.request is not None and self.request.method == 'POST'):
    #         return HabitSerializerToWrite
    #     return HabitSerializerToRead # MAYBE NOT NEEDED HERE
    
    # def perform_create(self, serializer):
    #     serializer.save(owner=self.request.user)

# PUT, PATCH, DELETE & GET (detailed) # MAYBE PUT AND PATCH NO SENSE ?? OR YES?
class AllHabitsDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RecurrentHabitSerializerToWrite

    def get_queryset(self):
        return RecurrentHabit.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if(self.request is not None and self.request.method == 'GET'):
            return HabitSerializerToRead
        return HabitSerializerToWrite

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
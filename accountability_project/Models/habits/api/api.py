from Models.habits.api.serializers import RecurrentHabitSerializerToRead, RecurrentHabitSerializerToWrite, GoalSerializerToRead, GoalSerializerToWrite
from Models.habits.models import BaseHabit, RecurrentHabit, Goal
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter

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

# GET & GET (detailed) 
class AllHabitsApiView(generics.GenericAPIView): 

    filter_backends = [OrderingFilter]
    ordering_fields = ['id', 'title', 'created_at', 'updated_at', 'type']

    def get(self, request, *args, **kwargs):
        context = {"request": request,}
        pk = kwargs.get('pk')
        # Get specific habit
        if pk:
            try:
                habit = BaseHabit.objects.get(pk=pk)
                if habit.type == 'recurrent':
                    habit_specific = RecurrentHabit.objects.get(pk=pk)
                    habit_serializer = RecurrentHabitSerializerToRead(habit_specific, context=context)
                else:
                    habit_specific = Goal.objects.get(pk=pk)
                    habit_serializer = GoalSerializerToRead(habit_specific, context=context) 
            except BaseHabit.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            return Response(habit_serializer.data)
        # Get all habits
        else: 
            # All Habits queryset
            all_habits = BaseHabit.objects.filter(owner=self.request.user).select_subclasses()
            filtered_habits = self.filter_queryset(all_habits)
            
            response_data = []
            for habit in filtered_habits:
                if habit.type == 'recurrent':
                    specific_serializer = RecurrentHabitSerializerToRead(habit, context=context)
                else:
                    specific_serializer = GoalSerializerToRead(habit, context=context)
                response_data.append(specific_serializer.data) 
            return Response(response_data)
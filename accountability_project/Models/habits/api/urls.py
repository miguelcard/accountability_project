from Models.habits.api.api import (RecurrentHabitApiView, RecurrentHabitDetailApiView, GoalApiView,
 GoalDetailApiView, AllHabitsApiView, GetAllHabitTagsApiView, CheckmarksDetailApiView, CheckmarksApiView, CheckmarksApiViewWithPagination, 
 MilestonesApiView, MilestonesApiViewWithPagination, MilestonesDetailApiView)
from django.urls import path

urlpatterns = [
    path('v1/habits/', AllHabitsApiView.as_view(), name='habits'),
    path('v1/habits/<int:pk>', AllHabitsApiView.as_view(), name='habits-detail'),
    path('v1/habits/recurrent/', RecurrentHabitApiView.as_view(), name='recurrent'),
    path('v1/habits/recurrent/<int:pk>', RecurrentHabitDetailApiView.as_view(), name='recurrent-detail'),
    path('v1/habits/goals/', GoalApiView.as_view(), name='goal'),
    path('v1/habits/goals/<int:pk>', GoalDetailApiView.as_view(), name='goal-detail'),
    path('v1/habits/tags/', GetAllHabitTagsApiView.as_view(), name='habit-tags'),
    # Nested paths
    path('v1/habits/<int:habit_pk>/checkmarks/', CheckmarksApiView.as_view(), name='habit-checkmarks-list'),
    path('v1/habits/<int:habit_pk>/checkmarks/paginated/', CheckmarksApiViewWithPagination.as_view(), name='habit-checkmarks-paginated-detail'),
    path('v1/habits/<int:habit_pk>/checkmarks/<int:pk>', CheckmarksDetailApiView.as_view(), name='habit-checkmarks-detail'),
    # next ones are the same as the two above, justa dding recurrent and goals to the path, but functionality does not change
    # for recurrent ones:
    path('v1/habits/recurrent/<int:habit_pk>/checkmarks/', CheckmarksApiView.as_view(), name='recurrent-habit-checkmarks-list'),
    path('v1/habits/recurrent/<int:habit_pk>/checkmarks/paginated/', CheckmarksApiViewWithPagination.as_view(), name='recurrent-habit-checkmarks-paginated-detail'),
    path('v1/habits/recurrent/<int:habit_pk>/checkmarks/<int:pk>', CheckmarksDetailApiView.as_view(), name='recurrent-habit-checkmarks-detail'),
    # for goals:
    path('v1/habits/goals/<int:habit_pk>/checkmarks/', CheckmarksApiView.as_view(), name='goal-habit-checkmarks-list'),
    path('v1/habits/goals/<int:habit_pk>/checkmarks/paginated/', CheckmarksApiViewWithPagination.as_view(), name='goal-habit-checkmarks-paginated-detail'),
    path('v1/habits/goals/<int:habit_pk>/checkmarks/<int:pk>', CheckmarksDetailApiView.as_view(), name='goal-habit-checkmarks-detail'),
    # for goals milestones (same as checkmarks)
    path('v1/habits/goals/<int:habit_pk>/milestones/', MilestonesApiView.as_view(), name='goal-habit-milestones-list'),
    path('v1/habits/goals/<int:habit_pk>/milestones/paginated/', MilestonesApiViewWithPagination.as_view(), name='goal-habit-milestones-paginated-detail'),
    path('v1/habits/goals/<int:habit_pk>/milestones/<int:pk>', MilestonesDetailApiView.as_view(), name='goal-habit-milestones-detail'),
]

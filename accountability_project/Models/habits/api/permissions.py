from rest_framework.permissions import BasePermission
from Models.habits.models import BaseHabit
from Models.spaces.models import SpaceRole

# Note: has_permission is called on all HTTP requests whereas, has_object_permission is called only for detail methods (GET, PUT, PATCH) so it can be that both are called
        
# ADD -> if in safe methods AND if in same space ...(he can view) -> add another permission for this
class IsOwnerOfParentHabit(BasePermission):

    message = 'You must be the owner of the parent of this object'

    def has_permission(self, request, view):
        habit_id = view.kwargs.get("habit_pk")
        try:
            BaseHabit.objects.get(id=habit_id, owner=view.request.user)
            return True
        except BaseHabit.DoesNotExist:
            return False

    def has_object_permission(self, request, view, obj):
        return (obj.habit.owner == request.user)

class UserBelongsToHabitSpaces(BasePermission):

    message = 'You are trying to link the habit to a Space where you do not belong / are not a member '

    def has_object_permission(self, request, view, obj):

        # habit_serializer_spaces are the habits listed in the JSON request body
        habit_serializer = view.get_serializer(data=request.data)
        habit_serializer.is_valid(raise_exception=True)
        habit_serializer_spaces = habit_serializer.validated_data['spaces']

        # getting the spaces where the user is a member:
        user_spaces = request.user.user_spaces.all()

        for habit_space in habit_serializer_spaces:
            if habit_space not in user_spaces:
                return False
        return True
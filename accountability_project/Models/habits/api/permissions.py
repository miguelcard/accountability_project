from rest_framework.permissions import BasePermission, SAFE_METHODS
from Models.habits.models import BaseHabit

# Note: has_permission is called on all HTTP requests whereas, has_object_permission is called only for detail methods (GET, PUT, PATCH) so it can be that both are called
        
# ADD -> if in safe methods AND if in same space ...(he can view) -> add another permission for this
class IsOwnerOfParentHabit(BasePermission):

    message = 'You must be the owner of the parent habit of this checkmark and the new checkmark body must have the habit id you own'

    def has_permission(self, request, view):
        habit_id = view.kwargs.get("habit_pk")
        try:
            habit = BaseHabit.objects.get(id=habit_id, owner=view.request.user.id)
        except BaseHabit.DoesNotExist:
            return False

        checkmark_serializer = view.get_serializer(data=request.data)
        checkmark_serializer.is_valid(raise_exception=True)
        serializer_habit = checkmark_serializer.validated_data['habit']
        
        return True if (habit == serializer_habit) else False


    def has_object_permission(self, request, view, obj):
        return (obj.habit.owner == request.user)


class UserBelongsToHabitSpaces(BasePermission):

    message = 'You are trying to link the habit to a Space where you do not belong / are not a member '

    # For POST
    def has_permission(self, request, view):
        return self.check_user_belongs_to_space_sent_in_habit_serializer(request, view)
        
    # For GET, PUT, PATCH
    def has_object_permission(self, request, view, obj):
        return self.check_user_belongs_to_space_sent_in_habit_serializer(request, view)


    def check_user_belongs_to_space_sent_in_habit_serializer(self, request, view):

        if request.method in SAFE_METHODS:
            return True

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

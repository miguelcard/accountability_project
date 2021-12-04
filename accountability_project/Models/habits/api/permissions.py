from rest_framework.permissions import BasePermission
from Models.habits.models import BaseHabit
from Models.habits.models import CheckMark

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

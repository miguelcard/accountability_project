from rest_framework.permissions import BasePermission
from rest_framework import permissions


class IsSpaceAdminOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow admins of a Space to edit it.
    Assumes the model instance has an `admin` attribute.
    """
    message = 'You must be the admin of this object to edit it'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Test code to delete
        foo = obj.spaceroles.filter(member=request.user, role='admin').exists()
        print(f'user: {request.user.username} has permission to edit: {foo}')
        # end of test code
        return obj.spaceroles.filter(member=request.user, role='admin').exists()



# Example:
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.owner == request.user

# Example: 
# class NameOfPermission(BasePermission):
    
#     message = 'You must be the owner of this object'

#     def has_permission(self, request, view):     
#         # no object specific checking       # A more generic permission (not per object)
#         habit_id = view.kwargs.get("habit_pk")
        # try:
        #     BaseHabit.objects.get(id=habit_id, owner=view.request.user)
        #     return True
        # except BaseHabit.DoesNotExist:
        #     return False
    
#     def has_object_permission(self, request, view, obj):
#         my_safe_methods = ['PUT']
#         if request.method in my_safe_methods:
#             return True
#         return obj.user == request.user
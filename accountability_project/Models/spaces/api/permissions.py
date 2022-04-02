from rest_framework.permissions import BasePermission
from rest_framework import permissions
from Models.spaces.models import SpaceRole

# Note: has_permission is called on all HTTP requests whereas, has_object_permission is called only for detail methods (GET, PUT, PATCH) so it can be that both are called

class IsSpaceAdminWhereSpaceRoleBelongsOrReadOnly(permissions.BasePermission):
    """
    Permission only for admins of a space based on a SpaceRole
    """
    message = 'You must be the admin of the Space to manage its SpaceRoles'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        space = obj.space
        return space.spaceroles.filter(member=request.user, role='admin').exists()


class BelongsToSpaceFromSpaceRole(permissions.BasePermission):
    """
    request user belongs to the space where the SpaceRole is being created
    """
    message = 'You must belong to the Space you are adding a role to'

    def has_permission(self, request, view):
        # from the serializer (SpaceRole) get space members, then compare request.user belongs there
        spacerole_serializer = view.get_serializer(data=request.data)
        spacerole_serializer.is_valid(raise_exception=True)
        space = spacerole_serializer.validated_data['space']

        for member in space.members.all():
            if member == request.user:
                return True
        return False


class HasEqualOrHigherRoleAsNewUser(permissions.BasePermission):
    """
    request user has equal or higher role than the new user in the serialiyer
    e.g. a user with "member" role would have no permission to add a user with "admin" role, only member
    """
    message = 'You must have equal or higher permission than the user you are adding'

    def has_permission(self, request, view):
        # from the serializer (SpaceRole) get role, then compare request.user has same or higher role in the Space
        spacerole_serializer = view.get_serializer(data=request.data)
        spacerole_serializer.is_valid(raise_exception=True)
        space = spacerole_serializer.validated_data['space']
        new_role = spacerole_serializer.validated_data['role']
        request_user_role = SpaceRole.objects.get(member=request.user, space=space).role

        if request_user_role == new_role or request_user_role == 'admin':
            return True 
        return False


# Examples:

# class IsSpaceObjectAdminOrReadOnly(permissions.BasePermission):
#     """
#     Object-level permission to only allow admins of a Space to edit it.
#     Assumes the model instance has an `admin` attribute.
#     """
#     message = 'You must be the admin of this object to edit it'

#     def has_object_permission(self, request, view, obj):
#         if request.method in permissions.SAFE_METHODS:
#             return True
#         # Test code to delete
#         foo = obj.spaceroles.filter(member=request.user, role='admin').exists()
#         print(f'user: {request.user.username} has permission to edit: {foo}')
#         # end of test code
#         return obj.spaceroles.filter(member=request.user, role='admin').exists()

# class IsOwnerOrReadOnly(permissions.BasePermission):
#     """
#     Object-level permission to only allow owners of an object to edit it.
#     Assumes the model instance has an `owner` attribute.
#     """

#     def has_object_permission(self, request, view, obj):
#         # Read permissions are allowed to any request,
#         # so we'll always allow GET, HEAD or OPTIONS requests.
#         if request.method in permissions.SAFE_METHODS:
#             return True

#         # Instance must have an attribute named `owner`.
#         return obj.owner == request.user

# Example: 
# class NameOfPermission(BasePermission):
    
#     message = 'You must be the owner of this object'

#     def has_permission(self, request, view):     
#         # no object specific checking  , A more generic permission (not per object)
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
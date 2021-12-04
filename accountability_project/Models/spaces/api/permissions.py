from rest_framework.permissions import BasePermission



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
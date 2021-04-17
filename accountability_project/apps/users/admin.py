from django.contrib import admin
from apps.users.models import User
from apps.groups.models import Group

admin.site.register(User)
admin.site.register(Group)
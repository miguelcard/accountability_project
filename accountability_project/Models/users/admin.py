from django.contrib import admin
from Models.users.models import User
from Models.groups.models import Group
from Models.scoreboards.models import Scoreboard
from Models.habits.models import Habit

admin.site.register(User)
admin.site.register(Group)
admin.site.register(Scoreboard)
admin.site.register(Habit)

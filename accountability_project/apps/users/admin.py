from django.contrib import admin
from apps.users.models import User
from apps.groups.models import Group
from apps.scoreboards.models import ScoreBoard
from apps.habits.models import Habit, StartDay, FinishDay

admin.site.register(User)
admin.site.register(Group)
admin.site.register(ScoreBoard)
admin.site.register(Habit)
admin.site.register(StartDay)
admin.site.register(FinishDay)

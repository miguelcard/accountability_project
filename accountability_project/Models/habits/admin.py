from django.contrib import admin
from Models.habits.models import BaseHabitSpace, RecurrentHabit, Goal, CheckMark, Milestone, HabitTag

# Register your models here.
admin.site.register(RecurrentHabit)
admin.site.register(Goal)
admin.site.register(CheckMark)
admin.site.register(Milestone)
admin.site.register(HabitTag)
admin.site.register(BaseHabitSpace)

from django.contrib import admin
from Models.habits.models import RecurrentHabit, Goal, CheckMark, Milestone

# Register your models here.
admin.site.register(RecurrentHabit)
admin.site.register(Goal)
admin.site.register(CheckMark)
admin.site.register(Milestone)


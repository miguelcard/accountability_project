from django.contrib import admin
from Models.habits.models import RecurrentHabit, Goal

# Register your models here.
admin.site.register(RecurrentHabit)
admin.site.register(Goal)


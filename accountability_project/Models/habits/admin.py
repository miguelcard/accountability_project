from django.contrib import admin
from Models.habits.models import RecurrentHabit, Goal

admin.site.register(RecurrentHabit, Goal)
# Register your models here.

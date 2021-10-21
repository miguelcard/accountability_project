from django.db.models.base import Model
from django.db.models.fields import CharField
from rest_framework.fields import ReadOnlyField
from Models.users.models import User
from Models.spaces.models import Space
from django.db import models
from model_utils.managers import InheritanceManager 
from datetime import date, datetime

# Tags for the habits
class HabitTag(models.Model):
    name = models.CharField(max_length=50, unique=True, blank=True, null=True)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Habit Tag'
        verbose_name_plural = 'Habit Tags'

# This Habit is an abstraction and the real implementation should be done either by recurrent habit or goal
class BaseHabit(models.Model):
    """Model definition for MODELNAME."""
    objects = InheritanceManager()

    owner = models.ForeignKey(User, on_delete=models.CASCADE) 
    tags = models.ManyToManyField(HabitTag, blank=True) 
    space = models.ManyToManyField(Space, blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    type = models.CharField(editable=False, max_length=11)

    def __str__(self):
        """Unicode representation of MODELNAME."""
        return f'{self.title}'
    
class RecurrentHabit(BaseHabit):
    TIME_FRAME_CHOICES = [
    ('W', 'Week'),
    ('M', 'Month'),
    ]
    # Here the user can set how many times per week/month to do the habit
    times = models.IntegerField()
    time_frame = models.CharField(max_length=1, choices=TIME_FRAME_CHOICES)  # Should these be made optional?
    
    def save(self, *args, **kwargs):
        self.type = 'recurrent'
        super(BaseHabit, self).save(*args, **kwargs) 
    
    class Meta:
        verbose_name = 'Recurrent Habit'
        verbose_name_plural = 'Recurrent Habits'
        ordering = ['-created_at']

class Goal(BaseHabit):

    start_date = models.DateTimeField(default=datetime.now, blank=True, null=True)
    finish_date = models.DateTimeField(blank=True, null=True) # If not filled, write in front end it is recomended!

    def save(self, *args, **kwargs):
        self.type = 'goal'
        super(BaseHabit, self).save(*args, **kwargs) 

    class Meta:
        verbose_name = 'Goal'
        verbose_name_plural = 'Goals'
        ordering = ['-created_at']

class CheckMark(models.Model):
    DATE_STATUS_CHOICES = [
    ('UNDEFINED', 'undefined'),
    ('NOT_PLANNED', 'not planned'),
    ('DONE', 'done'),
    ('NOT_DONE', 'not done'),
    ]
    date = models.DateTimeField()
    satus = models.CharField(max_length=13, choices=DATE_STATUS_CHOICES, default='UNDEFINED')
    habit = models.ForeignKey(BaseHabit, on_delete=models.CASCADE, related_name="checkmarks")
    
    class Meta:
        verbose_name = 'Check Mark'
        verbose_name_plural = 'Check Marks'
        ordering = ['-date']

class Milestone(models.Model):
    name = models.CharField(max_length= 70)
    description = models.TextField(max_length=200, blank=True, null=True)
    date = models.DateTimeField()
    habit = models.ForeignKey(Goal, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Milestone'
        verbose_name_plural = 'Milestones'
        ordering = ['-date']
    
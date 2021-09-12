from Models.users.models import Tag
from Models.users.models import User
from Models.spaces.models import Space
from django.db import models

# This Habit is an abstraction and the real implementation should be done either by recurrent habit or goal
class BaseHabit(models.Model):
    """Model definition for MODELNAME."""

    owner = models.ForeignKey(User, on_delete=models.CASCADE) 
    # in this case tags are same as user tags, but we can create different tags for habits
    tags = models.ManyToManyField(Tag, blank=True) 
    space = models.ManyToManyField(Space, blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        """Unicode representation of MODELNAME."""
        return f'{self.title}'

class RecurrentHabit(BaseHabit):
    TIME_FRAME_CHOICES = [
    ('W', 'Week'),
    ('M', 'Month'),
    ]
    times = models.IntegerField()
    time_frame = models.CharField(max_length=1, choices=TIME_FRAME_CHOICES)
    # Here the user can set how many times per week/month to do the habit

    class Meta:
        verbose_name = 'Recurrent Habit'
        verbose_name_plural = 'Recurrent Habits'

class Goal(BaseHabit):

    start_date = models.DateTimeField(blank=True, null=True) # Make default "today" from front-end
    finish_date = models.DateTimeField()

    class Meta:
        verbose_name = 'Goal'
        verbose_name_plural = 'Goals'

class CheckMark(models.Model):
    DATE_STATUS_CHOICES = [
    ('UNDEFINED', 'undefined'),
    ('NOT_PLANNED', 'not planned'),
    ('DONE', 'done'),
    ('NOT_DONE', 'not done'),
    ]
    date = models.DateTimeField()
    satus = models.CharField(max_length=13, choices=DATE_STATUS_CHOICES, default='UNDEFINED')
    habit = models.ForeignKey(BaseHabit, on_delete=models.CASCADE)

class Milestone():
    name = models.CharField(max_length= 70)
    description = models.TextField(max_length=200, blank=True, null=True)
    date = models.DateTimeField()
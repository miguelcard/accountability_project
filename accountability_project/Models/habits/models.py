from Models.users.models import Tag
from Models.users.models import User
from django.db import models

# This Habit is an abstraction and the real implementation should be done either by recurrent habit or goal
class BaseHabit(models.Model):
    """Model definition for MODELNAME."""

    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True, null=True) # in this case tags are same as user tags, but we can create different tags for habits
    # Add space here
    # For mapping back from one model to other see "symmetrical" and "related_name"

    title = models.CharField(max_length=100)
    description = models.TextField(max_length=255)
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

    start_date = models.DateTimeField(blank=True, null=True) # Make default today from front-end
    finish_date = models.DateTimeField()

    class Meta:
        verbose_name = 'Goal'
        verbose_name_plural = 'Goals'

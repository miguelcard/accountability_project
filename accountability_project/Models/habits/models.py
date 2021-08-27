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

    # start_day = models.DateTimeField(blank=True, null=True)
    # finish_day = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # class Meta:
    #     """Meta definition for MODELNAME."""
        
    #     verbose_name = 'Habit'
    #     verbose_name_plural = 'Habits'

    def __str__(self):
        """Unicode representation of MODELNAME."""
        return f'{self.title}'

class RecurrentHabit(BaseHabit):

    TIME_FRAME_CHOICES = [
    ('D', 'Daily'),
    ('W', 'Weekly'),
    ('M', 'Monthly'),
    ]
    time_frame = models.CharField(max_length=1, choices=TIME_FRAME_CHOICES, blank=True, null=True)
     # times ... think about this, how will it be chosen from front end ?  maybe delete one time frame (Monthly)

from rest_framework import status
from Models.users.models import User
from Models.spaces.models import Space
from django.db import models
from model_utils.managers import InheritanceManager 
import datetime
from utils.exceptionhandlers import BusinessLogicConflict

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

    class Meta:
        ordering = ['-created_at']

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

    start_date = models.DateField(default=datetime.date.today, blank=True, null=True)
    finish_date = models.DateField(blank=True, null=True) # If not filled, write in front end it is recomended!

    def save(self, *args, **kwargs):
        self.type = 'goal'
        if self.finish_date != None and self.start_date != None and self.finish_date < self.start_date:
            raise BusinessLogicConflict(detail='the finish_date must be greater than the start_date for a Goal')
        
        super(BaseHabit, self).save(*args, **kwargs) 

    class Meta:
        verbose_name = 'Goal'
        verbose_name_plural = 'Goals'
        ordering = ['-created_at']

class CheckMark(models.Model):
    STATUS_CHOICES = [
    ('UNDEFINED', 'undefined'),
    ('NOT_PLANNED', 'not planned'),
    ('DONE', 'done'),
    ('NOT_DONE', 'not done'),
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    date = models.DateField() #Default date should come from the front-end that knows the date and time of the client
    status = models.CharField(max_length=13, choices=STATUS_CHOICES, default='UNDEFINED')
    habit = models.ForeignKey(BaseHabit, on_delete=models.CASCADE, related_name="checkmarks")

    def save(self, *args, **kwargs):
        today = datetime.date.today()
        if self.date > today and self.status != 'UNDEFINED' and self.status != 'NOT_PLANNED':
            raise BusinessLogicConflict(detail='statuses DONE and NOT_DONE can not be set for future dates')
        
        same_date_checkmarks = CheckMark.objects.filter(habit=self.habit, date=self.date) 
        if same_date_checkmarks.exists():
            same_date_checkmarks.delete()
        super(CheckMark, self).save(*args, **kwargs) 
    
    class Meta:
        verbose_name = 'Check Mark'
        verbose_name_plural = 'Check Marks'
        ordering = ['-date']

class Milestone(models.Model):
    STATUS_CHOICES = [  
    ('DONE', 'done'),
    ('NOT_DONE', 'not done'),
    ]
    status = models.CharField(max_length=13, choices=STATUS_CHOICES, default='NOT_DONE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length= 70)
    description = models.TextField(max_length=200, blank=True, null=True)
    date = models.DateField()
    habit = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name="milestones")

    class Meta:
        verbose_name = 'Milestone'
        verbose_name_plural = 'Milestones'
        ordering = ['-date']
    
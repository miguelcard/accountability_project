from rest_framework import status
from Models.users.models import User
from Models.spaces.models import Space
from django.db import models, transaction
from model_utils.managers import InheritanceManager 
import datetime
from utils.exceptionhandlers import BusinessLogicConflict, LimitReachedException


# This Habit is an abstraction and the real implementation should be done either by recurrent habit or goal
class BaseHabit(models.Model):
    """ Abstract habit model extended by Goal and RecurrentHabit"""
    MAX_HABITS_PER_USER_PER_SPACE = 6

    objects = InheritanceManager()
    owner = models.ForeignKey(User, related_name='habits', on_delete=models.CASCADE) 
    tags = models.ManyToManyField('HabitTag', blank=True)
    spaces = models.ManyToManyField(Space, through='BaseHabitSpace', related_name='space_habits', blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    type = models.CharField(editable=False, max_length=11)

    class Meta:
        verbose_name = 'Base Habit'
        verbose_name_plural = 'Base Habits'
        ordering = ['-created_at']
        db_table = 'habit'

    def __str__(self):
        """Unicode representation of MODELNAME."""
        return f'{self.id} - {self.title}'
    
    # returns the first found space, useful for many to one relationship between habit and space.
    @property
    def space(self):
        # returns None if none exists
        return self.spaces.first()
    
class BaseHabitSpace(models.Model):
    """
    This is the join table between Habits and Spaces, which would normally represent a M2M relationship,
    but for now we enforce a M2O relationship as the application does not need more, by setting the FK column referencing the Habit to be unique.
    Maybe in the future this constraint can be dropped if we need a habit to belong to more than one space
    Here we can also possibly add more data about this habit and this space, like when was the habit added to the space and so on
    """
    basehabit = models.ForeignKey(BaseHabit, on_delete=models.CASCADE)
    space = models.ForeignKey(Space, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'space_habit'
        constraints = [
            models.UniqueConstraint(fields=['basehabit'], name='unique_basehabit_one_space'),
            models.UniqueConstraint(fields=['basehabit', 'space'], name='unique_basehabit_space_pair'), # this is a redundancy, it jus prevents duplicate rows with basehabit and space
        ]
        
    def clean(self):
        owner = self.basehabit.owner
        space_pk = self.space_id

        # exclude this habit itself (works for create & update)
        existing_habits_count = BaseHabit.objects.filter(
            owner=owner,
            spaces__pk=space_pk
        ).exclude(pk=self.basehabit_id).count()

        if existing_habits_count >= BaseHabit.MAX_HABITS_PER_USER_PER_SPACE:
            # tie the error to a field or use non_field_errors
            # This returns an ugly 500 error to the django admin, but thats ok for now
            raise LimitReachedException (
                code="FREE_HABIT_CREATE_LIMIT_REACHED", # maps with the frontend messages
                current=existing_habits_count,
                limit=BaseHabit.MAX_HABITS_PER_USER_PER_SPACE,
                detail=f"User already has {existing_habits_count} habits in space {space_pk} (max {BaseHabit.MAX_HABITS_PER_USER_PER_SPACE}).",
                instance=self,
                status_code=403
            )

    def save(self, *args, **kwargs):
        # Optional: wrap in atomic lock to reduce races (see notes below)
        with transaction.atomic():
            # Optionally acquire a row lock before counting to avoid a race condition.
            # A common choice is to lock the owner user row as a coarse mutex:
            # This lock just forces any other transaction that tries to use the same lock on that user, to wait until the whole transaction has been commited. (simply like a waiting point)
            # This is simpler than locking specific habit rows that the user owns in that space because it can happen that there are not any (therefore we do not lock anything) and we have to take into account all edge cases.
            # Const: possibly slower than blocking the habit rows.
            User.objects.select_for_update().get(pk=self.basehabit.owner_id)
            
            self.full_clean()   # runs clean() and field validators
            super().save(*args, **kwargs)
    

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
        db_table = 'recurrent_habit'

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
        db_table = 'goal'

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

    # Allow only one checkmark per day, i.e. delete any otheres that exist on the same day
    def save(self, *args, **kwargs):
        today = datetime.date.today()
        if self.date > today and self.status != 'UNDEFINED' and self.status != 'NOT_PLANNED':
            raise BusinessLogicConflict(detail='statuses DONE and NOT_DONE can not be set for future dates') # Should it be enabled?
        same_date_checkmarks = CheckMark.objects.filter(habit=self.habit, date=self.date) 
        if same_date_checkmarks.exists():
            same_date_checkmarks.delete()
        super(CheckMark, self).save(*args, **kwargs) 
    
    class Meta:
        verbose_name = 'Check Mark'
        verbose_name_plural = 'Check Marks'
        ordering = ['-date']
        db_table = 'checkmark'

    def __str__(self):
        return f'{self.date} - {self.status} - habit: ({self.habit})'

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
        db_table = 'milestone'
    
# Tags for the habits
class HabitTag(models.Model):
    name = models.CharField(max_length=50, unique=True, blank=True, null=True)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Habit Tag'
        verbose_name_plural = 'Habit Tags'
        ordering = ['name']
        db_table = 'habit_tag'
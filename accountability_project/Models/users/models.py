from datetime import date
from django.db import models
from django.db.models.base import Model
from Models.scoreboards.models import Scoreboard
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from simple_history.models import HistoricalRecords


class UserManager(BaseUserManager):
    """custom user"""
    def _create_user(self, username, email, name, last_name, password,  is_staff, is_superuser, **extra_fields):
        user = self.model(
            username = username,
            email = email,
            name = name,
            last_name = last_name,
            is_staff = is_staff,
            is_superuser = is_superuser,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, name, last_name, password=None, **extra_fields):
        return self._create_user(username, email, name, last_name, password, False, False, **extra_fields)

    def create_superuser(self, username, email, name=None, last_name=None, password=None, **extra_fields):
        return self._create_user(username, email, name, last_name, password, True, True, **extra_fields)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, blank=True, null=True)

class Language(models.Model):
    name = models.CharField(max_length=50, unique=True, blank=True, null=True)

    def __str__(self):
        return self.name

class User(AbstractBaseUser, PermissionsMixin):
    """create models for the database"""

    GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
    ]

    username = models.CharField('username', max_length=120, unique=True)
    name = models.CharField('your name', max_length=70, blank=True, null=True)
    last_name = models.CharField('last name', max_length=90, blank=True, null=True)
    email = models.EmailField('your email', max_length=255, unique=True)
    profile_photo = models.ImageField(upload_to='images/profile/', blank=True, null=True)
    birthdate = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=7, choices=GENDER_CHOICES, blank=True, null=True)
    about = models.CharField(max_length=280, blank=True, null=True)
    tags = models.ForeignKey(Tag, on_delete=models.PROTECT, blank=True, null=True)
    languages = models.ForeignKey(Language, on_delete=models.PROTECT, blank=True, null=True)
    score_board = models.ForeignKey(Scoreboard, on_delete=models.CASCADE,blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    historical = HistoricalRecords()
    objects = UserManager()

    class Meta:
        """meta caracters"""
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    @property
    def age(self):
        today = date.today()
        born = self.birthdate
        if born is None:
            return None
        rest = 1 if (today.month, today.day) < (born.month, born.day) else 0
        return today.year - born.year - rest

    def natural_key(self):
        return (self.username)

    def __str__(self):
        return f'{self.name} {self.last_name} {self.email} {self.created_at} {self.updated_at}'

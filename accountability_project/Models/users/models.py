
from django.db import models
from django.db.models.base import Model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from simple_history.models import HistoricalRecords


class UserManager(BaseUserManager):
    """custom user"""

    use_in_migrations = True

    def _create_user(self, username, email, name, password,  is_staff, is_superuser, **extra_fields):
        user = self.model(
            username = username,
            email = email,
            name = name,
            is_staff = is_staff,
            is_superuser = is_superuser,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, name, password=None, **extra_fields):
        return self._create_user(username, email, name, password, False, False, **extra_fields)

    def create_superuser(self, username, email, name=None, password=None, **extra_fields):
        return self._create_user(username, email, name, password, True, True, **extra_fields)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, blank=True, null=True)
    def __str__(self):
        return self.name

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
    name = models.CharField('first name', max_length=70, blank=True, null=True)
    email = models.EmailField('email', max_length=255, unique=True)
    avatar_seed = models.CharField('avatar seed', max_length=20, blank=True, null=True)
    birthdate = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=7, choices=GENDER_CHOICES, blank=True, null=True)
    about = models.CharField(max_length=280, blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    languages = models.ManyToManyField(Language, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    historical = HistoricalRecords(cascade_delete_history=True)
    objects = UserManager()

    class Meta:
        """meta caracters"""
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] # email field automatically included if its the USERNAME_FIELD

    def natural_key(self):
        return (self.username)

    def __str__(self):
        return f'[{str(self.id)}] {self.username} - {self.name} {self.email} {self.created_at} {self.updated_at}'

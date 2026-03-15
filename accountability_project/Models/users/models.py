
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from simple_history.models import HistoricalRecords


class UserManager(BaseUserManager):
    """Custom user manager supporting Firebase-based auth and Django admin superusers."""

    use_in_migrations = True

    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required for admin/superuser accounts.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)

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

    # --- Firebase fields --------------------------------------------------- #
    firebase_uid = models.CharField(
        'Firebase UID', max_length=128, unique=True, blank=True, null=True,
        help_text='UID provided by Firebase Authentication.',
    )
    is_anonymous_firebase_user = models.BooleanField(
        default=False,
        help_text='True when the user signed in anonymously via Firebase.',
    )

    # --- Legacy / transitional fields (deprecated — delete later) ---------- #
    username = models.CharField('username', max_length=120, unique=True, blank=True, null=True)
    name = models.CharField('first name', max_length=70, blank=True, null=True)
    email = models.EmailField('email', max_length=255, unique=True, blank=True, null=True)  # deprecated
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

    USERNAME_FIELD = 'email'  # Kept for Django admin / createsuperuser
    REQUIRED_FIELDS = []  # Only email + password prompted by createsuperuser

    def natural_key(self):
        return (self.firebase_uid or self.email,)

    def __str__(self):
        identifier = self.username or self.firebase_uid or self.email or 'no-id'
        return f'[{self.id}] {identifier} ({self.created_at})'


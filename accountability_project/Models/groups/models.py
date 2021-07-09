from django.db import models
from Models.users.models import User
from simple_history.models import HistoricalRecords
from django.db.models.fields.related import ForeignKey


class Post(models.Model):
    """ Model definitions for post table"""
    user_owner = ForeignKey(User,
                            on_delete=models.CASCADE,
                            null=False,
                            blank=False,
                            related_name='user')
    content = models.TextField('contents', max_length=255, blank=False, null=False)
    images = models.ImageField(upload_to='images/posts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Unicode representation of post table."""
        return f'{self.user_owner} {self.created_at} {self.updated_at}'


class Group(models.Model):
    """Model definition for MODELNAME"""

    admins = models.ManyToManyField(User, related_name='admins', blank=False)
    group_name = models.CharField('group name', max_length=200) #Not necessarily unique, the only unique distinnguisher will be the ID which is going to be given automatically by us
    theme = models.CharField('theme group', max_length=50)
    description = models.TextField('description', max_length=255, blank=True, null=True)
    users = models.ManyToManyField(User, related_name='users', blank=True)
    post = models.ForeignKey(Post, on_delete = models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    historical = HistoricalRecords()

    class Meta:
        """Meta definition for MODELNAME."""
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'

    REQUIRED_FIELDS = ['group_name']

    def __str__(self):
        """Unicode representation of MODELNAME."""
        return f'{self.group_name} {self.theme} {self.created_at} {self.updated_at}'
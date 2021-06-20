from django.db import models
from Models.users.models import User
from simple_history.models import HistoricalRecords



class Group(models.Model):
    """Model definition for MODELNAME."""

    group_name = models.CharField('group name', max_length=200) #Not necessaarily unique, the only unique distinnguisher will be the ID which is going to be given automatically by us
    theme = models.CharField('theme group', max_length=50)
    description = models.TextField('description', max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    users = models.ManyToManyField(User, related_name='users')
    historical = HistoricalRecords()

    class Meta:
        """Meta definition for MODELNAME."""
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'

    USERNAME_FIELD = 'group_name'
    REQUIRED_FIELDS = ['group_name', 'theme']

    def natural_key(self):
        return (self.group_name)

    def __str__(self):
        """Unicode representation of MODELNAME."""
        return f'{self.group_name} {self.theme} {self.created_at} {self.updated_at}'


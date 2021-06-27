from django.db import models
from Models.habits.models import Habit


class Scoreboard(models.Model):
    """Model definition for MODELNAME."""

    notes = models.TextField(max_length=255, blank=True, null=True)
    habit = models.ManyToManyField(Habit)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta definition for MODELNAME."""

        verbose_name = 'Scoreboard'
        verbose_name_plural = 'Scoreboards'

    def __str__(self):
        """Unicode representation of MODELNAME."""
        return f'{self.created_at} {self.updated_at}'



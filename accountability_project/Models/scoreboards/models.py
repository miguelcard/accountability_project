from django.db import models
from Models.habits.models import Habit


class ScoreBoard(models.Model):
    """Model definition for MODELNAME."""

    notes = models.TextField(max_length=255, blank=True, null=True)
    habit = models.ManyToManyField(Habit)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta definition for MODELNAME."""

        verbose_name = 'ScoreBoard'
        verbose_name_plural = 'ScoreBoards'

    def __str__(self):
        """Unicode representation of MODELNAME."""
        return f'{self.created_at} {self.updated_at}'



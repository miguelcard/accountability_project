from django.db import models

class Habit(models.Model):
    """Model definition for MODELNAME."""

    title = models.CharField(max_length=50)
    description = models.TextField(max_length=255)
    start_day = models.DateTimeField(blank=True, null=True)
    finish_day = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta definition for MODELNAME."""
        
        verbose_name = 'Habit'
        verbose_name_plural = 'Habits'

    def __str__(self):
        """Unicode representation of MODELNAME."""
        return f'{self.title}'

from django.db import models


class FinishDay(models.Model):
    """Model definition for MODELNAME."""

    day = models.IntegerField()
    month = models.IntegerField()
    year = models.IntegerField()

    class Meta:
        """Meta definition for MODELNAME."""

        verbose_name = 'FinishDay'
        verbose_name_plural = 'FinishDays'

    def __str__(self):
        """Unicode representation of MODELNAME."""
        return f':{self.day} :{self.month} :{self.year}'


class StartDay(models.Model):
    """Model definition for MODELNAME."""

    day = models.IntegerField()
    month = models.IntegerField()
    year = models.IntegerField()

    class Meta:
        """Meta definition for MODELNAME."""

        verbose_name = 'StartDay'
        verbose_name_plural = 'StartDays'

    def __str__(self):
        """Unicode representation of MODELNAME."""
        return f':{self.day} :{self.month} :{self.year}'


class Habit(models.Model):
    """Model definition for MODELNAME."""

    title = models.CharField(max_length=50)
    description = models.TextField(max_length=255)
    start_day = models.ForeignKey(StartDay, on_delete=models.CASCADE, null=False, blank=False)
    finish_day = models.ForeignKey(FinishDay, on_delete=models.CASCADE, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta definition for MODELNAME."""

        verbose_name = 'Habit'
        verbose_name_plural = 'Habits'

    def __str__(self):
        """Unicode representation of MODELNAME."""
        return f'{self.title}'

"""
Migration 0016 – RecurrentHabitConfigHistory

1. Creates the recurrent_habit_config_history table.
2. Back-fills one row per existing RecurrentHabit using its current times /
   time_frame values and its created_at date as effective_from.
"""

import django.db.models.deletion
import django.db.models.functions
import datetime
from django.db import migrations, models


def backfill_config_history(apps, schema_editor):
    RecurrentHabit = apps.get_model('habits', 'RecurrentHabit')
    ConfigHistory   = apps.get_model('habits', 'RecurrentHabitConfigHistory')

    entries = []
    for habit in RecurrentHabit.objects.all():
        entries.append(
            ConfigHistory(
                habit_id       = habit.pk,
                times          = habit.times,
                time_frame     = habit.time_frame,
                effective_from = habit.created_at.date(),
            )
        )
    if entries:
        ConfigHistory.objects.bulk_create(entries, ignore_conflicts=True)


def reverse_backfill(apps, schema_editor):
    # Data-only reverse: nothing to undo (table drop happens in DB op below)
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0015_xp_ledger'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecurrentHabitConfigHistory',
            fields=[
                ('id',             models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('times',          models.IntegerField()),
                ('time_frame',     models.CharField(max_length=1)),
                ('effective_from', models.DateField(help_text='First day on which this config applies (inclusive).')),
                ('habit',          models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='config_history',
                    to='habits.recurrenthabit',
                )),
            ],
            options={
                'verbose_name':        'Recurrent Habit Config History',
                'verbose_name_plural': 'Recurrent Habit Config Histories',
                'db_table':            'recurrent_habit_config_history',
                'ordering':            ['-effective_from'],
            },
        ),
        migrations.AddConstraint(
            model_name='recurrenthabitconfighistory',
            constraint=models.UniqueConstraint(
                fields=['habit', 'effective_from'],
                name='unique_config_per_habit_per_day',
            ),
        ),
        migrations.RunPython(backfill_config_history, reverse_backfill),
    ]

# Generated by Django 3.1.13 on 2021-10-06 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0009_recurrenthabit_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goal',
            name='finish_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

# Generated by Django 3.1.13 on 2021-12-04 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spaces', '0007_auto_20211204_1152'),
        ('habits', '0005_basehabit_space'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='basehabit',
            name='space',
        ),
        migrations.AddField(
            model_name='basehabit',
            name='spaces',
            field=models.ManyToManyField(blank=True, related_name='space_habits', to='spaces.Space'),
        ),
    ]

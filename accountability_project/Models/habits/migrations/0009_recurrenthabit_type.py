# Generated by Django 3.1.8 on 2021-10-02 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0008_auto_20211002_1817'),
    ]

    operations = [
        migrations.AddField(
            model_name='recurrenthabit',
            name='type',
            field=models.CharField(default='recurrent', editable=False, max_length=11),
        ),
    ]

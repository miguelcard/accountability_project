# Generated by Django 3.1.13 on 2021-11-01 18:03

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0012_auto_20211101_1003'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goal',
            name='start_date',
            field=models.DateField(blank=True, default=datetime.date.today, null=True),
        ),
    ]

# Generated by Django 3.1.8 on 2021-06-18 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0002_auto_20210524_1201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='group_name',
            field=models.CharField(max_length=200, verbose_name='group name'),
        ),
        migrations.AlterField(
            model_name='historicalgroup',
            name='group_name',
            field=models.CharField(max_length=200, verbose_name='group name'),
        ),
    ]

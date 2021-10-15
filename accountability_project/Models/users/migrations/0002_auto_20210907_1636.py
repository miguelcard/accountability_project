# Generated by Django 3.1.8 on 2021-09-07 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='languages',
            field=models.ManyToManyField(blank=True, null=True, to='users.Language'),
        ),
        migrations.AlterField(
            model_name='user',
            name='tags',
            field=models.ManyToManyField(blank=True, null=True, to='users.Tag'),
        ),
    ]
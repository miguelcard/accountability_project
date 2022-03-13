# Generated by Django 3.1.13 on 2021-11-28 13:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('spaces', '0002_auto_20211118_1807'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpaceRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('admin', 'admin'), ('member', 'member')], max_length=30)),
            ],
            options={
                'verbose_name': 'Space Role',
                'verbose_name_plural': 'Space Roles',
                'db_table': 'role',
                'ordering': ['name'],
            },
        ),
        migrations.RemoveField(
            model_name='space',
            name='roles',
        ),
        migrations.AlterModelTable(
            name='space',
            table='space',
        ),
        migrations.DeleteModel(
            name='Role',
        ),
        migrations.AddField(
            model_name='spacerole',
            name='space',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spaces.space'),
        ),
        migrations.AddField(
            model_name='spacerole',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.RemoveField(
            model_name='space',
            name='users',
        ),
        migrations.AddField(
            model_name='space',
            name='users',
            field=models.ManyToManyField(related_name='user_spaces', through='spaces.SpaceRole', to=settings.AUTH_USER_MODEL),
        ),
    ]
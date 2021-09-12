# Generated by Django 3.1.8 on 2021-09-12 13:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('habits', '0004_auto_20210910_0732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basehabit',
            name='description',
            field=models.TextField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='basehabit',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user'),
        ),
        migrations.CreateModel(
            name='CheckMark',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('satus', models.CharField(choices=[('UNDEFINED', 'undefined'), ('NOT_PLANNED', 'not planned'), ('DONE', 'done'), ('NOT_DONE', 'not done')], default='UNDEFINED', max_length=13)),
                ('habit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='habits.basehabit')),
            ],
        ),
    ]

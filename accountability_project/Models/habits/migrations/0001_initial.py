# Generated by Django 3.1.7 on 2021-04-20 06:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FinishDay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.IntegerField()),
                ('month', models.IntegerField()),
                ('year', models.IntegerField()),
            ],
            options={
                'verbose_name': 'FinishDay',
                'verbose_name_plural': 'FinishDays',
            },
        ),
        migrations.CreateModel(
            name='StardDay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.IntegerField()),
                ('month', models.IntegerField()),
                ('year', models.IntegerField()),
            ],
            options={
                'verbose_name': 'StartDay',
                'verbose_name_plural': 'StartDays',
            },
        ),
        migrations.CreateModel(
            name='Habit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('description', models.TextField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('finish_day', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='habits.finishday')),
                ('start_day', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='habits.stardday')),
            ],
            options={
                'verbose_name': 'Habit',
                'verbose_name_plural': 'Habits',
            },
        ),
    ]
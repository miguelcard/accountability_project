# Generated by Django 3.1.13 on 2023-11-16 21:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('spaces', '0012_auto_20231115_0655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spacerole',
            name='member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='spaceroles', to=settings.AUTH_USER_MODEL),
        ),
    ]

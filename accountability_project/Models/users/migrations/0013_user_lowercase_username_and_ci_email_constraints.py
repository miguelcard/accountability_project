import django.db.models.functions.text
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Enforce at the database level what the application already guarantees:
    - a stored username is always lowercase. Together with the existing unique index on
      username this also makes usernames unique ignoring case, and it makes exact lookups
      on lowercased input safe.
    - an email is unique ignoring case, so case-insensitive email lookups never match two users.

    Fails (and rolls back) if existing emails collide ignoring case; fix those rows first.
    """

    dependencies = [
        ('users', '0012_lowercase_usernames'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='user',
            constraint=models.CheckConstraint(
                condition=models.Q(username=django.db.models.functions.text.Lower('username')),
                name='user_username_is_lowercase',
            ),
        ),
        migrations.AddConstraint(
            model_name='user',
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower('email'),
                name='user_email_ci_unique',
            ),
        ),
    ]

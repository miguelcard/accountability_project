from collections import defaultdict

from django.db import migrations


def lowercase_usernames(apps, schema_editor):
    User = apps.get_model('users', 'User')

    users_by_lowered = defaultdict(list)
    for user in User.objects.exclude(username__isnull=True).exclude(username=''):
        users_by_lowered[user.username.strip().lower()].append(user)

    collisions = {
        lowered: [u.username for u in users]
        for lowered, users in users_by_lowered.items()
        if len(users) > 1
    }
    if collisions:
        raise RuntimeError(
            'Cannot lowercase usernames, these would collide: '
            + ', '.join(f'{lowered} <- {originals}' for lowered, originals in collisions.items())
            + '. Rename the affected users manually and re-run the migration.'
        )

    for lowered, users in users_by_lowered.items():
        user = users[0]
        if user.username != lowered:
            # queryset.update() bypasses save(), history signals and auto_now
            User.objects.filter(pk=user.pk).update(username=lowered)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_historicaluser_firebase_uid_and_more'),
    ]

    operations = [
        migrations.RunPython(lowercase_usernames, migrations.RunPython.noop),
    ]

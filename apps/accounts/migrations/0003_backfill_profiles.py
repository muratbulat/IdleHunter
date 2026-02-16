# Backfill UserProfile for users that don't have one (e.g. created before accounts app)

from django.conf import settings
from django.db import migrations


def backfill_profiles(apps, schema_editor):
    User = apps.get_model(settings.AUTH_USER_MODEL)
    UserProfile = apps.get_model("accounts", "UserProfile")
    Role = apps.get_model("accounts", "Role")
    viewer = Role.objects.filter(name="viewer").first()
    for user in User.objects.all():
        UserProfile.objects.get_or_create(user=user, defaults={"role": viewer})


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_default_roles"),
    ]

    operations = [
        migrations.RunPython(backfill_profiles, noop),
    ]

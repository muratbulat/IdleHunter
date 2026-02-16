# Data migration: create default RBAC roles

from django.db import migrations


def create_roles(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")
    for name, desc in [
        ("viewer", "View dashboard and read-only data"),
        ("operator", "View and run scans"),
        ("admin", "Full access including data sources and users"),
    ]:
        Role.objects.get_or_create(name=name, defaults={"description": desc})


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_roles, noop),
    ]

# Add default Celery Beat schedule: daily run_scan at 02:00 UTC
from django.db import migrations


def add_daily_scan(apps, schema_editor):
    CrontabSchedule = apps.get_model("django_celery_beat", "CrontabSchedule")
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute="0",
        hour="2",
        day_of_week="*",
        day_of_month="*",
        month_of_year="*",
        timezone="UTC",
    )
    PeriodicTask.objects.get_or_create(
        name="IdleHunter daily scan (all sources)",
        defaults={
            "task": "apps.scans.tasks.run_scan",
            "crontab": schedule,
            "enabled": True,
            "kwargs": "{}",
        },
    )


def remove_daily_scan(apps, schema_editor):
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    PeriodicTask.objects.filter(name="IdleHunter daily scan (all sources)").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("scans", "0001_initial"),
        ("django_celery_beat", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_daily_scan, remove_daily_scan),
    ]

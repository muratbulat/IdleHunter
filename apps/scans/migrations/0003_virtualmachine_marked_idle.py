# Generated migration: add user-marked idle flag to VirtualMachine

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scans", "0002_add_daily_scan_schedule"),
    ]

    operations = [
        migrations.AddField(
            model_name="virtualmachine",
            name="marked_idle",
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]

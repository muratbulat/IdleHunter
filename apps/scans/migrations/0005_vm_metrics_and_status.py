# Resource-based idle detection: metrics and status (active/idle/missing)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scans", "0004_idle_score_replace_marked_idle"),
    ]

    operations = [
        migrations.AddField(
            model_name="virtualmachine",
            name="status",
            field=models.CharField(
                choices=[
                    ("active", "Active"),
                    ("idle", "Idle"),
                    ("missing", "Missing"),
                ],
                db_index=True,
                default="active",
                help_text="active=in use; idle=low/no usage; missing=not seen in recent scans",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="virtualmachine",
            name="power_state",
            field=models.CharField(blank=True, max_length=32),
        ),
        migrations.AddField(
            model_name="virtualmachine",
            name="last_boot_time",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="virtualmachine",
            name="uptime_days",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="virtualmachine",
            name="cpu_usage_mhz",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="virtualmachine",
            name="cpu_usage_percent",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="virtualmachine",
            name="memory_usage_mb",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="virtualmachine",
            name="network_usage_kbps",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="virtualmachine",
            name="disk_usage_iops",
            field=models.FloatField(blank=True, null=True),
        ),
    ]

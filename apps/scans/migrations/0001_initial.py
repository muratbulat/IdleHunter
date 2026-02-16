# Generated for IdleHunter scans app
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DataSource",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(help_text="Display name for this source", max_length=255)),
                ("source_type", models.CharField(choices=[("vcenter", "vCenter"), ("aria", "VMware Aria"), ("stor2rrd", "Stor2RRD")], db_index=True, max_length=20)),
                ("is_enabled", models.BooleanField(default=True)),
                ("config", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "verbose_name": "Data source",
                "verbose_name_plural": "Data sources",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="ScanRun",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("running", "Running"), ("success", "Success"), ("failed", "Failed")], db_index=True, default="pending", max_length=20)),
                ("message", models.TextField(blank=True)),
                ("data_source", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="scan_runs", to="scans.datasource")),
            ],
            options={
                "verbose_name": "Scan run",
                "verbose_name_plural": "Scan runs",
                "ordering": ["-started_at"],
            },
        ),
        migrations.CreateModel(
            name="VirtualMachine",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(db_index=True, max_length=255)),
                ("uuid", models.CharField(db_index=True, max_length=64, unique=True)),
                ("last_seen", models.DateTimeField(blank=True, null=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("data_source", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="virtual_machines", to="scans.datasource")),
            ],
            options={
                "verbose_name": "Virtual machine",
                "verbose_name_plural": "Virtual machines",
                "ordering": ["name"],
            },
        ),
        migrations.AddConstraint(
            model_name="virtualmachine",
            constraint=models.UniqueConstraint(fields=("data_source", "uuid"), name="scans_virtualmachine_unique_ds_uuid"),
        ),
    ]

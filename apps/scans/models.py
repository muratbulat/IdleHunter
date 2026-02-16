# Scans app: data sources, virtual machines, scan runs
from django.db import models

from apps.core.models import TimeStampedModel


class DataSource(TimeStampedModel):
    """External data source: vCenter, VMware Aria, or Stor2RRD."""

    class SourceType(models.TextChoices):
        VCENTER = "vcenter", "vCenter"
        ARIA = "aria", "VMware Aria"
        STOR2RRD = "stor2rrd", "Stor2RRD"

    name = models.CharField(max_length=255, help_text="Display name for this source")
    source_type = models.CharField(
        max_length=20, choices=SourceType.choices, db_index=True
    )
    is_enabled = models.BooleanField(default=True)
    # Connection details stored as JSON or in env; for Step 2 we only store metadata.
    config = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Data source"
        verbose_name_plural = "Data sources"

    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"


class VirtualMachine(TimeStampedModel):
    """VM discovered from a data source; used for resource-based idle scoring."""

    class VMStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        IDLE = "idle", "Idle"
        MISSING = "missing", "Missing"

    data_source = models.ForeignKey(
        DataSource, on_delete=models.CASCADE, related_name="virtual_machines"
    )
    name = models.CharField(max_length=255, db_index=True)
    uuid = models.CharField(max_length=64, unique=True, db_index=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    # Resource-based idle score 0.0 (active) to 1.0 (idle); null = not yet computed
    idle_score = models.FloatField(null=True, blank=True, db_index=True)
    # Distinguish idle (low resource use) from missing (not seen in scans)
    status = models.CharField(
        max_length=20,
        choices=VMStatus.choices,
        default=VMStatus.ACTIVE,
        db_index=True,
        help_text="active=in use; idle=low/no usage; missing=not seen in recent scans",
    )
    # Performance metrics from last scan (for resource-based idle detection)
    power_state = models.CharField(max_length=32, blank=True)  # poweredOn, poweredOff
    last_boot_time = models.DateTimeField(null=True, blank=True)
    uptime_days = models.FloatField(null=True, blank=True)
    cpu_usage_mhz = models.FloatField(null=True, blank=True)
    cpu_usage_percent = models.FloatField(null=True, blank=True)
    memory_usage_mb = models.FloatField(null=True, blank=True)
    network_usage_kbps = models.FloatField(null=True, blank=True)
    disk_usage_iops = models.FloatField(null=True, blank=True)
    # Raw snapshot of last-known state (cluster, etc.)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Virtual machine"
        verbose_name_plural = "Virtual machines"
        unique_together = [["data_source", "uuid"]]

    def __str__(self):
        return f"{self.name} ({self.uuid[:8]}...)"


class ScanRun(TimeStampedModel):
    """A single run of data collection (vCenter/Aria/Stor2RRD) and optional scoring."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    data_source = models.ForeignKey(
        DataSource, on_delete=models.CASCADE, null=True, blank=True, related_name="scan_runs"
    )
    message = models.TextField(blank=True)  # Error or summary message

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "Scan run"
        verbose_name_plural = "Scan runs"

    def __str__(self):
        return f"ScanRun {self.started_at.isoformat()} ({self.status})"

# Idle VM detection: resource-based (weighted scoring) + missing/deleted
from django.conf import settings
from django.utils import timezone

from .models import VirtualMachine

# Days without being seen in a scan → treat as missing/deleted
MISSING_DAYS_THRESHOLD = getattr(settings, "IDLE_DAYS_THRESHOLD", 7)
# Powered-off VMs: if last boot was more than this many days ago → definitely idle
POWEREDOFF_IDLE_DAYS = getattr(settings, "POWEREDOFF_IDLE_DAYS", 30)
# Resource thresholds for "idle" (poweredOn but no usage)
CPU_IDLE_PERCENT = getattr(settings, "CPU_IDLE_PERCENT_THRESHOLD", 5.0)
NETWORK_IDLE_KBPS = getattr(settings, "NETWORK_IDLE_KBPS_THRESHOLD", 1.0)
DISK_IDLE_IOPS = getattr(settings, "DISK_IDLE_IOPS_THRESHOLD", 5.0)


def compute_idle_scores(queryset=None):
    """
    Set idle_score and status on VMs using:
    - Missing: last_seen too old or None → status='missing', idle_score=1.0
    - Rule A (Zombie): power_state=='poweredOff' and last_boot_time > 30 days ago → 1.0, status='idle'
    - Rule B (Idle): power_state=='poweredOn' → weighted score from low CPU/network/disk; status from score.
    """
    if queryset is None:
        queryset = VirtualMachine.objects.all()
    now = timezone.now()
    updated = 0
    fields = [
        "pk", "last_seen", "idle_score", "status",
        "power_state", "last_boot_time", "cpu_usage_percent",
        "network_usage_kbps", "disk_usage_iops",
    ]
    for vm in queryset.only(*fields):
        new_status = VirtualMachine.VMStatus.ACTIVE
        new_score = 0.0

        # --- Missing: not seen in recent scans (deleted or not collected) ---
        if vm.last_seen is None or (now - vm.last_seen).days >= MISSING_DAYS_THRESHOLD:
            new_status = VirtualMachine.VMStatus.MISSING
            new_score = 1.0
        else:
            # --- Rule A: Powered-off "zombie" (off for a long time) ---
            power = (vm.power_state or "").strip().lower()
            if power == "poweredoff":
                last_boot = vm.last_boot_time
                if last_boot is not None and (now - last_boot).days > POWEREDOFF_IDLE_DAYS:
                    new_status = VirtualMachine.VMStatus.IDLE
                    new_score = 1.0
                # else: recently powered off; leave active/0.0 or could treat as idle
            else:
                # --- Rule B: Powered-on; score by resource usage (current snapshot) ---
                # Uses latest metrics; 7-day average would require metric history table.
                if power == "poweredon":
                    points = 0.0
                    if vm.cpu_usage_percent is not None and vm.cpu_usage_percent < CPU_IDLE_PERCENT:
                        points += 0.4
                    if vm.network_usage_kbps is not None and vm.network_usage_kbps < NETWORK_IDLE_KBPS:
                        points += 0.3
                    if vm.disk_usage_iops is not None and vm.disk_usage_iops < DISK_IDLE_IOPS:
                        points += 0.2
                    new_score = min(points, 1.0)
                    new_status = (
                        VirtualMachine.VMStatus.IDLE
                        if new_score >= 0.5
                        else VirtualMachine.VMStatus.ACTIVE
                    )

        if vm.idle_score != new_score or vm.status != new_status:
            vm.idle_score = new_score
            vm.status = new_status
            vm.save(update_fields=["idle_score", "status"])
            updated += 1
    return updated


def run_detection(data_source_id=None):
    """
    Run resource-based idle detection on all VMs or only for a given DataSource.
    Returns number of VMs updated.
    """
    if data_source_id is not None:
        qs = VirtualMachine.objects.filter(data_source_id=data_source_id)
    else:
        qs = VirtualMachine.objects.all()
    return compute_idle_scores(qs)

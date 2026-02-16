# Base interface for data source clients; VM and metric DTOs.
from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Optional


@dataclass
class VMInfo:
    """VM info from any source (vCenter, Aria, Stor2RRD) including metrics for idle detection."""
    name: str
    uuid: str
    power_state: Optional[str] = None  # e.g. poweredOn, poweredOff
    metadata: Optional[dict] = None  # source-specific (cluster, cpu, memory, etc.)
    # Resource metrics for idle scoring (use latest snapshot; 7-day avg would need history)
    cpu_usage_mhz: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    network_usage_kbps: Optional[float] = None
    disk_usage_iops: Optional[float] = None
    uptime_days: Optional[float] = None
    last_boot_time: Optional[datetime] = None  # when VM was last booted (runtime.bootTime)


@dataclass
class VMMetrics:
    """Metrics for idle scoring: CPU, memory, disk I/O (optional)."""
    vm_id: str  # uuid or source id
    cpu_percent: Optional[float] = None
    memory_mb: Optional[float] = None
    memory_percent: Optional[float] = None
    disk_io_read_kbps: Optional[float] = None
    disk_io_write_kbps: Optional[float] = None
    sampled_at: Optional[str] = None  # ISO datetime
    metadata: Optional[dict] = None


class BaseClient:
    """Abstract base for vCenter, Aria, Stor2RRD clients."""

    def get_vms(self, config: dict) -> List[VMInfo]:
        """List VMs from the source. config: host, user, password key, etc."""
        raise NotImplementedError

    def get_vm_metrics(self, config: dict, vm_id: str) -> Optional[VMMetrics]:
        """Fetch metrics for one VM (optional; Aria/Stor2RRD)."""
        return None

# vCenter 8.x API client via pyvmomi
# Lists VMs with name, uuid, power state, QuickStats (CPU, memory), boot time.
import os
import ssl
from datetime import datetime, timezone
from typing import Any, List

from .base import BaseClient, VMInfo

try:
    from pyVim.connect import SmartConnect, Disconnect
    from pyVmomi import vim
    PYVMOMI_AVAILABLE = True
except ImportError:
    PYVMOMI_AVAILABLE = False

# Default MHz per core to derive CPU % when not available (e.g. 2 GHz)
DEFAULT_MHZ_PER_CORE = 2000.0


def _get_password(config: dict) -> str:
    """Get password from env using config key (e.g. password_env_key)."""
    key = config.get("password_env_key") or "VCENTER_PASSWORD"
    return os.environ.get(key, "")


def _pyvmomi_time_to_datetime(t) -> datetime | None:
    """Convert pyvmomi datetime (e.g. bootTime) to timezone-aware datetime."""
    if t is None:
        return None
    try:
        # pyvmomi returns datetime with timezone or naive
        if hasattr(t, "isoformat"):
            return t
        return None
    except Exception:
        return None


class VCenterClient(BaseClient):
    """vCenter 8.x client using pyvmomi. Fetches VMs with QuickStats and boot time for idle detection."""

    def get_vms(self, config: dict) -> List[VMInfo]:
        if not PYVMOMI_AVAILABLE:
            return []
        host = config.get("host") or os.environ.get("VCENTER_HOST", "")
        user = config.get("user") or os.environ.get("VCENTER_USER", "")
        password = config.get("password") or _get_password(config)
        port = int(config.get("port") or os.environ.get("VCENTER_PORT", "443"))
        if not host or not user or not password:
            return []
        context = ssl.create_default_context()
        if not os.environ.get("VCENTER_SSL_VERIFY", "").lower() in ("1", "true", "yes"):
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        try:
            si = SmartConnect(
                host=host,
                user=user,
                pwd=password,
                port=port,
                sslContext=context,
            )
            try:
                content = si.RetrieveContent()
                container = content.rootFolder
                view_type = [vim.VirtualMachine]
                recursive = True
                view = content.viewManager.CreateContainerView(container, view_type, recursive)
                vms: List[VMInfo] = []
                for vm in view.view:
                    name = getattr(vm, "name", None) or ""
                    uuid = ""
                    metadata = {}
                    num_cpu = None
                    memory_size_mb = None
                    if hasattr(vm, "summary") and vm.summary and hasattr(vm.summary, "config") and vm.summary.config:
                        uuid = getattr(vm.summary.config, "uuid", None) or ""
                        num_cpu = getattr(vm.summary.config, "numCpu", None)
                        memory_size_mb = getattr(vm.summary.config, "memorySizeMB", None)
                        metadata["numCpu"] = num_cpu
                        metadata["memorySizeMB"] = memory_size_mb
                    if not uuid and hasattr(vm, "config") and vm.config:
                        uuid = getattr(vm.config, "uuid", None) or ""

                    power = ""
                    last_boot_time = None
                    if hasattr(vm, "runtime") and vm.runtime:
                        ps = getattr(vm.runtime, "powerState", None)
                        power = str(ps).replace("PowerState.", "").strip().lower() if ps is not None else ""
                        boot_time = getattr(vm.runtime, "bootTime", None)
                        if boot_time is not None:
                            try:
                                last_boot_time = boot_time
                                if last_boot_time.tzinfo is None:
                                    last_boot_time = last_boot_time.replace(tzinfo=timezone.utc)
                            except Exception:
                                last_boot_time = None

                    cpu_usage_mhz = None
                    cpu_usage_percent = None
                    memory_usage_mb = None
                    uptime_days = None
                    if hasattr(vm, "summary") and vm.summary and hasattr(vm.summary, "quickStats") and vm.summary.quickStats:
                        qs = vm.summary.quickStats
                        cpu_usage_mhz = getattr(qs, "overallCpuUsage", None)
                        memory_usage_mb = getattr(qs, "guestMemoryUsage", None)
                        if memory_usage_mb is not None and memory_size_mb and memory_size_mb > 0:
                            metadata["memoryUsagePercent"] = round(100.0 * memory_usage_mb / memory_size_mb, 2)
                        if cpu_usage_mhz is not None and num_cpu and num_cpu > 0:
                            mhz_per_core = DEFAULT_MHZ_PER_CORE
                            cpu_usage_percent = min(100.0, 100.0 * cpu_usage_mhz / (num_cpu * mhz_per_core))
                        if last_boot_time is not None:
                            delta = (datetime.now(timezone.utc) - last_boot_time).total_seconds()
                            uptime_days = delta / (24.0 * 3600.0)

                    vms.append(VMInfo(
                        name=name,
                        uuid=uuid or f"vm-{id(vm)}",
                        power_state=power or None,
                        metadata=metadata or None,
                        cpu_usage_mhz=cpu_usage_mhz,
                        cpu_usage_percent=cpu_usage_percent,
                        memory_usage_mb=float(memory_usage_mb) if memory_usage_mb is not None else None,
                        network_usage_kbps=None,  # would require PerformanceManager
                        disk_usage_iops=None,    # would require PerformanceManager
                        uptime_days=uptime_days,
                        last_boot_time=last_boot_time,
                    ))
                view.Destroy()
                return vms
            finally:
                Disconnect(si)
        except Exception:
            return []


def get_vcenter_vms(config: dict) -> List[VMInfo]:
    """Convenience: list VMs from vCenter using config dict."""
    return VCenterClient().get_vms(config)

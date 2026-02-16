# Celery tasks: fetch VMs from vCenter/Aria/Stor2RRD and orchestrate scans
import json
from typing import List

from celery import shared_task
from django.core.cache import cache
from django.utils import timezone

from apps.integrations.aria import AriaClient
from apps.integrations.base import VMInfo
from apps.integrations.stor2rrd import Stor2RRDClient
from apps.integrations.vcenter import VCenterClient

from .detection import run_detection
from .models import DataSource, ScanRun, VirtualMachine

# Cache TTL for API responses (seconds) to avoid hammering external APIs
API_CACHE_TTL = 300


def _get_datasource_config(data_source: DataSource) -> dict:
    """Build config dict from DataSource (config JSON + env keys)."""
    cfg = dict(data_source.config or {})
    return cfg


def _cache_key(prefix: str, data_source_id: int, extra: str = "") -> str:
    return f"idlehunter:{prefix}:ds{data_source_id}:{extra}"


def _update_vms_from_list(data_source_id: int, vms: List[VMInfo]) -> int:
    """Create or update VirtualMachine records with metrics; return count."""
    try:
        ds = DataSource.objects.get(pk=data_source_id)
    except DataSource.DoesNotExist:
        return 0
    now = timezone.now()
    count = 0
    for vm in vms:
        if not vm.uuid:
            continue
        metadata = vm.metadata or {}
        defaults = {
            "name": vm.name or vm.uuid[:8],
            "last_seen": now,
            "power_state": vm.power_state or "",
            "last_boot_time": getattr(vm, "last_boot_time", None),
            "uptime_days": getattr(vm, "uptime_days", None),
            "cpu_usage_mhz": getattr(vm, "cpu_usage_mhz", None),
            "cpu_usage_percent": getattr(vm, "cpu_usage_percent", None),
            "memory_usage_mb": getattr(vm, "memory_usage_mb", None),
            "network_usage_kbps": getattr(vm, "network_usage_kbps", None),
            "disk_usage_iops": getattr(vm, "disk_usage_iops", None),
            "metadata": {**metadata, "power_state": vm.power_state},
        }
        obj, created = VirtualMachine.objects.update_or_create(
            data_source=ds,
            uuid=vm.uuid,
            defaults=defaults,
        )
        count += 1
    return count


def _vms_to_cache_items(vms: List[VMInfo]) -> list:
    """Serialize VMInfo list for Redis cache (include metrics)."""
    out = []
    for v in vms:
        item = {
            "name": v.name,
            "uuid": v.uuid,
            "power_state": v.power_state,
            "metadata": v.metadata,
            "cpu_usage_mhz": getattr(v, "cpu_usage_mhz", None),
            "cpu_usage_percent": getattr(v, "cpu_usage_percent", None),
            "memory_usage_mb": getattr(v, "memory_usage_mb", None),
            "network_usage_kbps": getattr(v, "network_usage_kbps", None),
            "disk_usage_iops": getattr(v, "disk_usage_iops", None),
            "uptime_days": getattr(v, "uptime_days", None),
            "last_boot_time": getattr(v, "last_boot_time", None),
        }
        if item["last_boot_time"] is not None and hasattr(item["last_boot_time"], "isoformat"):
            item["last_boot_time"] = item["last_boot_time"].isoformat()
        out.append(item)
    return out


def _vms_from_cache_items(items: list) -> List[VMInfo]:
    """Deserialize VMInfo list from cache."""
    from datetime import datetime
    vms = []
    for d in items:
        lb = d.get("last_boot_time")
        if isinstance(lb, str):
            try:
                lb = datetime.fromisoformat(lb.replace("Z", "+00:00"))
            except Exception:
                lb = None
        vms.append(VMInfo(
            name=d["name"],
            uuid=d["uuid"],
            power_state=d.get("power_state"),
            metadata=d.get("metadata"),
            cpu_usage_mhz=d.get("cpu_usage_mhz"),
            cpu_usage_percent=d.get("cpu_usage_percent"),
            memory_usage_mb=d.get("memory_usage_mb"),
            network_usage_kbps=d.get("network_usage_kbps"),
            disk_usage_iops=d.get("disk_usage_iops"),
            uptime_days=d.get("uptime_days"),
            last_boot_time=lb,
        ))
    return vms


def _fetch_vcenter_impl(data_source_id: int) -> dict:
    cache_key = _cache_key("vcenter", data_source_id)
    cached = cache.get(cache_key)
    if cached is not None:
        vms = _vms_from_cache_items(json.loads(cached))
    else:
        try:
            ds = DataSource.objects.get(pk=data_source_id, source_type=DataSource.SourceType.VCENTER)
        except DataSource.DoesNotExist:
            return {"ok": False, "error": "DataSource not found", "count": 0}
        config = _get_datasource_config(ds)
        vms = VCenterClient().get_vms(config)
        cache.set(cache_key, json.dumps(_vms_to_cache_items(vms)), API_CACHE_TTL)
    count = _update_vms_from_list(data_source_id, vms)
    return {"ok": True, "count": count}


def _fetch_aria_impl(data_source_id: int) -> dict:
    cache_key = _cache_key("aria", data_source_id)
    cached = cache.get(cache_key)
    if cached is not None:
        vms = _vms_from_cache_items(json.loads(cached))
    else:
        try:
            ds = DataSource.objects.get(pk=data_source_id, source_type=DataSource.SourceType.ARIA)
        except DataSource.DoesNotExist:
            return {"ok": False, "error": "DataSource not found", "count": 0}
        config = _get_datasource_config(ds)
        vms = AriaClient().get_vms(config)
        cache.set(cache_key, json.dumps(_vms_to_cache_items(vms)), API_CACHE_TTL)
    count = _update_vms_from_list(data_source_id, vms)
    return {"ok": True, "count": count}


def _fetch_stor2rrd_impl(data_source_id: int) -> dict:
    cache_key = _cache_key("stor2rrd", data_source_id)
    cached = cache.get(cache_key)
    if cached is not None:
        vms = _vms_from_cache_items(json.loads(cached))
    else:
        try:
            ds = DataSource.objects.get(pk=data_source_id, source_type=DataSource.SourceType.STOR2RRD)
        except DataSource.DoesNotExist:
            return {"ok": False, "error": "DataSource not found", "count": 0}
        config = _get_datasource_config(ds)
        vms = Stor2RRDClient().get_vms(config)
        cache.set(cache_key, json.dumps(_vms_to_cache_items(vms)), API_CACHE_TTL)
    count = _update_vms_from_list(data_source_id, vms)
    return {"ok": True, "count": count}


@shared_task(bind=True)
def fetch_vcenter_vms(self, data_source_id: int) -> dict:
    """Fetch VMs from a vCenter DataSource and sync to DB. Uses cache."""
    return _fetch_vcenter_impl(data_source_id)


@shared_task(bind=True)
def fetch_aria_vms(self, data_source_id: int) -> dict:
    """Fetch VMs from a VMware Aria DataSource and sync to DB."""
    return _fetch_aria_impl(data_source_id)


@shared_task(bind=True)
def fetch_stor2rrd_vms(self, data_source_id: int) -> dict:
    """Fetch VMs/clients from a Stor2RRD DataSource and sync to DB."""
    return _fetch_stor2rrd_impl(data_source_id)


@shared_task(bind=True)
def run_scan(self, data_source_id: int | None = None) -> dict:
    """
    Orchestrate a full scan: optionally for one DataSource or all enabled.
    Creates a ScanRun per source (or one global if data_source_id is None and we run all).
    """
    now = timezone.now()
    if data_source_id is not None:
        try:
            ds = DataSource.objects.get(pk=data_source_id, is_enabled=True)
        except DataSource.DoesNotExist:
            return {"ok": False, "error": "DataSource not found"}
        sources = [ds]
    else:
        sources = list(DataSource.objects.filter(is_enabled=True))

    results = []
    for ds in sources:
        scan_run = ScanRun.objects.create(
            data_source=ds,
            status=ScanRun.Status.RUNNING,
            started_at=now,
        )
        try:
            if ds.source_type == DataSource.SourceType.VCENTER:
                out = _fetch_vcenter_impl(ds.id)
            elif ds.source_type == DataSource.SourceType.ARIA:
                out = _fetch_aria_impl(ds.id)
            elif ds.source_type == DataSource.SourceType.STOR2RRD:
                out = _fetch_stor2rrd_impl(ds.id)
            else:
                out = {"ok": False, "error": f"Unknown source type {ds.source_type}", "count": 0}
            scan_run.finished_at = timezone.now()
            scan_run.status = ScanRun.Status.SUCCESS if out.get("ok") else ScanRun.Status.FAILED
            scan_run.message = out.get("message", str(out.get("count", 0)) + " VMs" if out.get("ok") else out.get("error", ""))
        except Exception as e:
            scan_run.finished_at = timezone.now()
            scan_run.status = ScanRun.Status.FAILED
            scan_run.message = str(e)
            out = {"ok": False, "error": str(e)}
        # Run idle detection on this source's VMs after fetch
        if out.get("ok"):
            run_detection(data_source_id=ds.id)
        results.append({"data_source_id": ds.id, "scan_run_id": scan_run.id, "result": out})
    return {"ok": True, "results": results}

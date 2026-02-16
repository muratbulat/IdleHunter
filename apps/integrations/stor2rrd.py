# Stor2RRD API client
# Fetches storage I/O or VM-related metrics. Adapt to your Stor2RRD API/version.
import os
from typing import Any, List, Optional

import requests

from .base import BaseClient, VMInfo, VMMetrics

REQUEST_TIMEOUT = 30


def _get_stor2rrd_config(config: dict) -> dict:
    """Build Stor2RRD connection params from config + env."""
    base_url = (
        config.get("base_url")
        or config.get("url")
        or os.environ.get("STOR2RRD_URL", "")
    ).rstrip("/")
    api_key = config.get("api_key") or os.environ.get("STOR2RRD_API_KEY", "")
    return {"base_url": base_url, "api_key": api_key}


class Stor2RRDClient(BaseClient):
    """
    Stor2RRD REST/client for storage and VM I/O metrics.
    Endpoints depend on Stor2RRD version; this is a stub that can be extended.
    """

    def get_vms(self, config: dict) -> List[VMInfo]:
        """List VMs or datastore clients from Stor2RRD if the API supports it."""
        cfg = _get_stor2rrd_config(config)
        if not cfg["base_url"]:
            return []
        headers = {"Content-Type": "application/json"}
        if cfg.get("api_key"):
            headers["X-API-Key"] = cfg["api_key"]
        # Stor2RRD may expose VM list via a specific endpoint; placeholder
        url = f"{cfg['base_url']}/api/vms"
        try:
            r = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            if r.status_code != 200:
                return []
            try:
                data = r.json()
            except Exception:
                return []
            vms = []
            items = data if isinstance(data, list) else (data.get("vms", []) if isinstance(data, dict) else [])
            for item in items:
                if isinstance(item, dict):
                    vms.append(VMInfo(
                        name=item.get("name", ""),
                        uuid=item.get("uuid", item.get("id", "")),
                        metadata=item,
                    ))
            return vms
        except Exception:
            return []

    def get_vm_metrics(self, config: dict, vm_id: str) -> Optional[VMMetrics]:
        """Fetch storage I/O metrics for a VM/datastore."""
        cfg = _get_stor2rrd_config(config)
        if not cfg["base_url"] or not vm_id:
            return None
        headers = {"Content-Type": "application/json"}
        if cfg.get("api_key"):
            headers["X-API-Key"] = cfg["api_key"]
        url = f"{cfg['base_url']}/api/vms/{vm_id}/metrics"
        try:
            r = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            if r.status_code != 200:
                return None
            data = r.json()
            if not isinstance(data, dict):
                return None
            return VMMetrics(
                vm_id=vm_id,
                disk_io_read_kbps=data.get("read_kbps"),
                disk_io_write_kbps=data.get("write_kbps"),
                metadata=data,
            )
        except Exception:
            return None


def get_stor2rrd_vms(config: dict) -> List[VMInfo]:
    """Convenience: list VMs/clients from Stor2RRD."""
    return Stor2RRDClient().get_vms(config)

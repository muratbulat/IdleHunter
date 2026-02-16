# VMware Aria (vRealize Operations) REST client
# Fetches metrics relevant to idle detection (CPU, memory, disk I/O).
# API: VMware Aria Operations 8.x REST API.
import os
from typing import Any, List, Optional

import requests

from .base import BaseClient, VMInfo, VMMetrics

# Default timeout for API calls
REQUEST_TIMEOUT = 30


def _get_aria_config(config: dict) -> dict:
    """Build Aria connection params from config + env."""
    base_url = (
        config.get("base_url")
        or config.get("url")
        or os.environ.get("ARIA_URL", "")
    ).rstrip("/")
    token = config.get("token") or os.environ.get("ARIA_TOKEN", "")
    user = config.get("user") or os.environ.get("ARIA_USER", "")
    password = config.get("password") or os.environ.get("ARIA_PASSWORD", "")
    return {"base_url": base_url, "token": token, "user": user, "password": password}


class AriaClient(BaseClient):
    """
    VMware Aria Operations REST client.
    Lists resources (VMs) and fetches metrics (CPU, memory, disk I/O).
    See: VMware Aria Operations REST API documentation.
    """

    def get_vms(self, config: dict) -> List[VMInfo]:
        """List VM-like resources from Aria. Returns minimal VMInfo list."""
        cfg = _get_aria_config(config)
        if not cfg["base_url"]:
            return []
        headers = self._auth_headers(cfg)
        # Aria API: adapter kind for vCenter; fetch resources of type VirtualMachine
        # Endpoint varies by Aria version; placeholder for /api/resources or similar
        url = f"{cfg['base_url']}/api/resources"
        try:
            r = requests.get(
                url,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
                params={"resourceKind": "VirtualMachine", "pageSize": 1000},
            )
            if r.status_code != 200:
                return []
            try:
                data = r.json()
            except Exception:
                return []
            vms = []
            resource_list = data.get("resourceList", []) if isinstance(data, dict) else []
            if not resource_list and isinstance(data, list):
                resource_list = data
            for res in resource_list:
                if isinstance(res, dict):
                    vms.append(VMInfo(
                        name=res.get("name", res.get("resourceKey", {}).get("name", "")),
                        uuid=res.get("identifier", {}).get("uuid", res.get("resourceId", "") or ""),
                        power_state=res.get("resourceStatusStates", {}).get("powerState"),
                        metadata=res,
                    ))
            return vms
        except Exception:
            return []

    def get_vm_metrics(self, config: dict, vm_id: str) -> Optional[VMMetrics]:
        """Fetch current metrics for one VM (CPU, memory, disk I/O)."""
        cfg = _get_aria_config(config)
        if not cfg["base_url"] or not vm_id:
            return None
        headers = self._auth_headers(cfg)
        # Placeholder: Aria metrics endpoint; adjust to actual API
        url = f"{cfg['base_url']}/api/resources/{vm_id}/metrics/latest"
        try:
            r = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            if r.status_code != 200:
                return None
            data = r.json()
            if not isinstance(data, dict):
                return None
            # Map common metric keys (adapt to Aria metric keys)
            values = data.get("values", data)
            return VMMetrics(
                vm_id=vm_id,
                cpu_percent=values.get("cpu|usage_average") or values.get("cpu_usage"),
                memory_mb=values.get("mem|consumed_average") or values.get("memory_consumed"),
                memory_percent=values.get("mem|usage_average") or values.get("memory_usage"),
                disk_io_read_kbps=values.get("disk|read_average") or values.get("disk_read"),
                disk_io_write_kbps=values.get("disk|write_average") or values.get("disk_write"),
                metadata=data,
            )
        except Exception:
            return None

    def _auth_headers(self, cfg: dict) -> dict:
        """Return headers with auth (token or basic)."""
        if cfg.get("token"):
            return {"Authorization": f"Bearer {cfg['token']}", "Content-Type": "application/json"}
        if cfg.get("user") and cfg.get("password"):
            import base64
            b64 = base64.b64encode(f"{cfg['user']}:{cfg['password']}".encode()).decode()
            return {"Authorization": f"Basic {b64}", "Content-Type": "application/json"}
        return {"Content-Type": "application/json"}


def get_aria_vms(config: dict) -> List[VMInfo]:
    """Convenience: list VMs from VMware Aria."""
    return AriaClient().get_vms(config)

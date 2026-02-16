# Load demo data: DataSources, VirtualMachines, ScanRuns
# Usage: python manage.py load_demo_data [--clear]
import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.scans.models import DataSource, ScanRun, VirtualMachine


DEMO_PREFIX = "Demo "


def make_uuid(seed: str) -> str:
    """Deterministic fake UUID-like string for demo."""
    h = abs(hash(seed)) % (16**12)
    return f"42000000-0000-0000-0000-{h:012x}"


class Command(BaseCommand):
    help = "Load demo data: DataSources, VirtualMachines, ScanRuns. Use --clear to remove demo data first."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Remove existing demo data (names starting with 'Demo ') before loading.",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self._clear_demo_data()
        self._load_datasources()
        self._load_vms()
        self._load_scan_runs()
        self.stdout.write(self.style.SUCCESS("Demo data loaded successfully."))

    def _clear_demo_data(self):
        # Delete VMs and ScanRuns for demo DataSources, then demo DataSources
        demo_sources = DataSource.objects.filter(name__startswith=DEMO_PREFIX)
        ids = list(demo_sources.values_list("id", flat=True))
        VirtualMachine.objects.filter(data_source_id__in=ids).delete()
        ScanRun.objects.filter(data_source_id__in=ids).delete()
        demo_sources.delete()
        self.stdout.write("Cleared existing demo data.")

    def _load_datasources(self):
        sources = [
            {
                "name": f"{DEMO_PREFIX}vCenter Lab",
                "source_type": DataSource.SourceType.VCENTER,
                "config": {"host": "vcenter-demo.example.com", "user": "administrator@vsphere.local", "password_env_key": "VCENTER_PASSWORD"},
            },
            {
                "name": f"{DEMO_PREFIX}VMware Aria",
                "source_type": DataSource.SourceType.ARIA,
                "config": {"base_url": "https://aria-demo.example.com", "token": ""},
            },
            {
                "name": f"{DEMO_PREFIX}Stor2RRD",
                "source_type": DataSource.SourceType.STOR2RRD,
                "config": {"base_url": "https://stor2rrd-demo.example.com"},
            },
        ]
        for s in sources:
            obj, _ = DataSource.objects.get_or_create(
                name=s["name"],
                defaults={"source_type": s["source_type"], "config": s["config"], "is_enabled": True},
            )
            self._demo_datasource_ids = getattr(self, "_demo_datasource_ids", []) + [obj.id]
        self.stdout.write(f"  Data sources: {len(sources)}")

    def _load_vms(self):
        if not getattr(self, "_demo_datasource_ids", None):
            ds = DataSource.objects.filter(name__startswith=DEMO_PREFIX).first()
            self._demo_datasource_ids = [ds.id] if ds else []
        if not self._demo_datasource_ids:
            return
        now = timezone.now()
        vm_templates = [
            ("WEB-SRV-01", 4, 8192, "poweredOn"),
            ("WEB-SRV-02", 2, 4096, "poweredOn"),
            ("DB-PROD-01", 8, 32768, "poweredOn"),
            ("DB-PROD-02", 8, 32768, "poweredOn"),
            ("APP-TEST-01", 2, 4096, "poweredOn"),
            ("APP-TEST-02", 2, 2048, "poweredOff"),
            ("FILE-01", 2, 4096, "poweredOn"),
            ("FILE-02", 2, 4096, "poweredOff"),
            ("LEGACY-XP", 1, 1024, "poweredOn"),
            ("LEGACY-2003", 1, 512, "poweredOff"),
            ("JUMP-BOX", 2, 2048, "poweredOn"),
            ("MONITOR-01", 2, 4096, "poweredOn"),
            ("IDLE-DEV-01", 2, 2048, "poweredOn"),
            ("IDLE-DEV-02", 2, 2048, "poweredOff"),
            ("BACKUP-PROXY", 4, 8192, "poweredOn"),
        ]
        created = 0
        # (name, cpus, mem_mb, power, cpu_%, net_kbps, disk_iops); low metrics => idle
        vm_specs = [
            ("WEB-SRV-01", 4, 8192, "poweredon", 25.0, 100.0, 50.0),
            ("WEB-SRV-02", 2, 4096, "poweredon", 12.0, 80.0, 30.0),
            ("DB-PROD-01", 8, 32768, "poweredon", 60.0, 200.0, 500.0),
            ("DB-PROD-02", 8, 32768, "poweredon", 55.0, 150.0, 400.0),
            ("APP-TEST-01", 2, 4096, "poweredon", 8.0, 5.0, 10.0),
            ("APP-TEST-02", 2, 2048, "poweredoff", None, None, None),
            ("FILE-01", 2, 4096, "poweredon", 3.0, 2.0, 8.0),
            ("FILE-02", 2, 4096, "poweredoff", None, None, None),
            ("LEGACY-XP", 1, 1024, "poweredon", 2.0, 0.5, 1.0),
            ("LEGACY-2003", 1, 512, "poweredoff", None, None, None),
            ("JUMP-BOX", 2, 2048, "poweredon", 1.0, 0.2, 2.0),
            ("MONITOR-01", 2, 4096, "poweredon", 15.0, 50.0, 20.0),
            ("IDLE-DEV-01", 2, 2048, "poweredon", 2.0, 0.3, 3.0),
            ("IDLE-DEV-02", 2, 2048, "poweredoff", None, None, None),
            ("BACKUP-PROXY", 4, 8192, "poweredon", 40.0, 300.0, 200.0),
        ]
        for ds_id in self._demo_datasource_ids:
            ds = DataSource.objects.get(pk=ds_id)
            for i, row in enumerate(vm_specs):
                name, cpu, mem_mb, power, cpu_pct, net_kbps, disk_iops = row
                uuid = make_uuid(f"{ds_id}-{name}-{i}")
                days_ago = random.randint(0, 14)
                last_seen = now - timedelta(days=days_ago) if days_ago > 0 else now
                # For poweredOff: last_boot > 30 days ago => Rule A (idle 1.0)
                if power == "poweredoff":
                    last_boot = now - timedelta(days=45) if name in ("IDLE-DEV-02", "LEGACY-2003", "FILE-02") else now - timedelta(days=10)
                    uptime_days = None
                else:
                    last_boot = now - timedelta(days=random.randint(1, 14))
                    uptime_days = (now - last_boot).total_seconds() / (24 * 3600)
                defaults = {
                    "name": name,
                    "last_seen": last_seen,
                    "power_state": power,
                    "last_boot_time": last_boot,
                    "uptime_days": uptime_days,
                    "cpu_usage_percent": cpu_pct,
                    "memory_usage_mb": (mem_mb * 0.4) if cpu_pct is not None else None,
                    "network_usage_kbps": net_kbps,
                    "disk_usage_iops": disk_iops,
                    "metadata": {"numCpu": cpu, "memorySizeMB": mem_mb, "power_state": power},
                }
                _, was_created = VirtualMachine.objects.update_or_create(
                    data_source=ds,
                    uuid=uuid,
                    defaults=defaults,
                )
                if was_created:
                    created += 1
        self.stdout.write(f"  Virtual machines: {len(self._demo_datasource_ids) * len(vm_specs)} total ({created} new)")

    def _load_scan_runs(self):
        if not getattr(self, "_demo_datasource_ids", None):
            demo = DataSource.objects.filter(name__startswith=DEMO_PREFIX)
            self._demo_datasource_ids = list(demo.values_list("id", flat=True))
        if not self._demo_datasource_ids:
            return
        now = timezone.now()
        for ds_id in self._demo_datasource_ids:
            ds = DataSource.objects.get(pk=ds_id)
            # 5 successful runs
            for i in range(5):
                started = now - timedelta(days=i + 1)
                ScanRun.objects.get_or_create(
                    data_source=ds,
                    started_at=started,
                    defaults={
                        "started_at": started,
                        "status": ScanRun.Status.SUCCESS,
                        "finished_at": started + timedelta(minutes=2),
                        "message": "15 VMs synced",
                    },
                )
            # 1 failed run
            failed_start = now - timedelta(days=6)
            ScanRun.objects.get_or_create(
                data_source=ds,
                started_at=failed_start,
                defaults={
                    "started_at": failed_start,
                    "status": ScanRun.Status.FAILED,
                    "finished_at": failed_start + timedelta(seconds=30),
                    "message": "Connection timeout (demo)",
                },
            )
        self.stdout.write(f"  Scan runs: {len(self._demo_datasource_ids) * 6} (5 success + 1 failed per source)")

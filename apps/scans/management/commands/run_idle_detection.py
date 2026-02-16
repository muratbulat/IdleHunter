# Run idle detection on all VMs (rule-based: no activity for IDLE_DAYS_THRESHOLD days = idle)
# Usage: python manage.py run_idle_detection

from django.core.management.base import BaseCommand

from apps.scans.detection import run_detection


class Command(BaseCommand):
    help = "Run idle detection on all VMs and set idle_score (1.0 = idle, 0.0 = active)."

    def handle(self, *args, **options):
        updated = run_detection()
        self.stdout.write(self.style.SUCCESS(f"Idle detection done. Updated {updated} VM(s)."))

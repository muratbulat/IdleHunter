# IdleHunter Celery application
# Broker and result backend are set from Django settings.
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("idlehunter")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """Placeholder task for testing Celery is working."""
    print(f"Request: {self.request!r}")

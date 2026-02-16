# IdleHunter config package
# Ensures Celery app is loaded when Django starts (for worker/beat)
from .celery import app as celery_app

__all__ = ("celery_app",)

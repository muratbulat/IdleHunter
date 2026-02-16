# IdleHunter - Settings for Docker Compose (web, celery_worker, celery_beat)
# Uses PostgreSQL and Redis from compose; env from .env / compose environment.
from .base import *  # noqa: F401, F403

DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

# Database must be set by compose (DATABASE_URL or POSTGRES_*)
# Redis and Celery URLs are passed by compose

# Security in production: set CSRF_TRUSTED_ORIGINS in .env
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

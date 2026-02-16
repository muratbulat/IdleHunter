# IdleHunter - Local development settings
# Use: DJANGO_SETTINGS_MODULE=config.settings.development (default in manage.py)
from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

# Optional: use SQLite if DATABASE_URL and POSTGRES_HOST are not set (see base.py)

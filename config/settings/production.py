# IdleHunter - Production settings
# Use: DJANGO_SETTINGS_MODULE=config.settings.production
from .base import *  # noqa: F401, F403

DEBUG = False
# ALLOWED_HOSTS must be set via env in production

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

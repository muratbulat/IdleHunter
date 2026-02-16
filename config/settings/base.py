# IdleHunter - Base Django settings
# Shared across all environments. Use env vars via django-environ.
import os
from pathlib import Path

import environ

# Project root (parent of config/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
    SECRET_KEY=(str, "django-insecure-change-me"),
    DATABASE_URL=(str, ""),
    REDIS_URL=(str, "redis://127.0.0.1:6379/0"),
    CELERY_BROKER_URL=(str, "redis://127.0.0.1:6379/1"),
    CELERY_RESULT_BACKEND=(str, "redis://127.0.0.1:6379/2"),
)

# Read .env from project root (optional)
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(str(env_file))

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Celery
    "django_celery_results",
    "django_celery_beat",
    # REST API & Swagger
    "rest_framework",
    "drf_yasg",
    # IdleHunter apps
    "apps.core",
    "apps.scans",
    "apps.accounts",
    "apps.integrations",
    "apps.web",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Database: prefer DATABASE_URL; fallback to POSTGRES_* or SQLite for local dev
_database_url = env("DATABASE_URL")
if _database_url:
    DATABASES = {"default": env.db("DATABASE_URL")}
else:
    _pg_user = os.environ.get("POSTGRES_USER", "idlehunter")
    _pg_pass = os.environ.get("POSTGRES_PASSWORD", "change-me")
    _pg_db = os.environ.get("POSTGRES_DB", "idlehunter")
    _pg_host = os.environ.get("POSTGRES_HOST", "localhost")
    _pg_port = os.environ.get("POSTGRES_PORT", "5432")
    if _pg_host and _pg_host != "localhost":
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": _pg_db,
                "USER": _pg_user,
                "PASSWORD": _pg_pass,
                "HOST": _pg_host,
                "PORT": _pg_port,
            }
        }
    else:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization (default: Turkish; English secondary)
LANGUAGE_CODE = env("LANGUAGE_CODE", default="tr")
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
LANGUAGES = [
    ("tr", "Türkçe"),
    ("en", "English"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]

# Static files (leading slash required so admin/icons load at /static/... from any page)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

# Celery (broker/backend from env in base)
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_RESULT_EXTENDED = True

# Celery Beat: use DB for schedule (django_celery_beat)
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# Cache: Redis for API response caching (short TTL in tasks)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env("REDIS_URL"),
    }
}

# CSRF (set in production/docker if needed)
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# Authentication: login redirects and backends
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/dashboard/"  # After login, go to NOC dashboard
LOGOUT_REDIRECT_URL = "/accounts/login/"

AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]
if env("LDAP_SERVER_URI", default=""):
    try:
        from config.settings.ldap import *  # noqa: F401, F403
        AUTHENTICATION_BACKENDS.insert(0, "django_auth_ldap.backend.LDAPBackend")
    except ImportError:
        pass

# MFA: enable/disable via env (default False for easier local dev)
ENABLE_MFA = env.bool("ENABLE_MFA", default=False)

# Idle detection: resource-based + missing
IDLE_DAYS_THRESHOLD = env.int("IDLE_DAYS_THRESHOLD", default=7)  # days not seen => missing
POWEREDOFF_IDLE_DAYS = env.int("POWEREDOFF_IDLE_DAYS", default=30)  # Rule A: off > N days => idle
CPU_IDLE_PERCENT_THRESHOLD = env.float("CPU_IDLE_PERCENT_THRESHOLD", default=5.0)
NETWORK_IDLE_KBPS_THRESHOLD = env.float("NETWORK_IDLE_KBPS_THRESHOLD", default=1.0)
DISK_IDLE_IOPS_THRESHOLD = env.float("DISK_IDLE_IOPS_THRESHOLD", default=5.0)
if ENABLE_MFA:
    INSTALLED_APPS.append("mfa")
    MFA_UNALLOWED_VIEW = "mfa.views.login"
    MFA_LOGIN_CALLBACK = "mfa.views.login"

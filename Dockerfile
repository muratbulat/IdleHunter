# IdleHunter - Production Dockerfile
# Python 3.12, Django, Gunicorn

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies (psycopg, python-ldap, gettext for i18n)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libldap2-dev \
    libsasl2-dev \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code (must include apps/, config/, manage.py)
COPY . .
RUN test -d /app/apps && test -d /app/config && test -f /app/templates/home.html || (echo "ERROR: Build context missing apps/, config/, or templates/home.html. Copy full project before docker build." && exit 1)
# Normalize line endings (Windows CRLF -> LF) and make entrypoint executable
RUN sed -i 's/\r$//' /app/entrypoint.sh 2>/dev/null || true && chmod +x /app/entrypoint.sh

# Bake static files and compile translations (Turkish default) into image
ENV DJANGO_SETTINGS_MODULE=config.settings.base
RUN mkdir -p /app/staticfiles && python manage.py collectstatic --noinput --no-color 2>/dev/null || true \
    && python manage.py compilemessages -i env 2>/dev/null || true

# Create non-root user for running the app
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
# Default: run Gunicorn (overridden in compose for celery_worker / celery_beat)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "config.wsgi:application"]

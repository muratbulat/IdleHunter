#!/bin/sh
# Run migrations and collect static files, then start the main command (e.g. Gunicorn).
set -e
echo "Running migrations..."
python manage.py migrate --noinput
echo "Collecting static files..."
python manage.py collectstatic --noinput --no-color 2>/dev/null || true
echo "Compiling translations..."
python manage.py compilemessages -i env 2>/dev/null || true
exec "$@"

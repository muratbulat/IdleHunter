#!/usr/bin/env bash
# IdleHunter - Deploy on this server (run ON the host where the project lives).
# Usage: cd /path/to/IdleHunter && ./scripts/deploy-on-server.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example. Edit .env and set SECRET_KEY, POSTGRES_PASSWORD, ALLOWED_HOSTS, then run this script again."
  exit 1
fi

echo "=== IdleHunter: Deploy on this server ==="
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

echo ""
echo "App: http://$(hostname -I | awk '{print $1}'):8000"
echo "Superuser: docker compose exec web python manage.py createsuperuser"

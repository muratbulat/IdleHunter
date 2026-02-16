#!/usr/bin/env bash
# IdleHunter - Deploy (build + up) on a host with Docker Compose
# Usage: ./scripts/deploy.sh [prod]
#   prod = use docker-compose.prod.yml for restart policies

set -e
cd "$(dirname "$0")/.."

COMPOSE_FILES="-f docker-compose.yml"
if [[ "${1:-}" == "prod" ]]; then
  COMPOSE_FILES="-f docker-compose.yml -f docker-compose.prod.yml"
fi

echo "Building and starting IdleHunter..."
docker compose $COMPOSE_FILES up -d --build

echo "Done. Run 'docker compose exec web python manage.py createsuperuser' if first deploy."

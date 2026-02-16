#!/usr/bin/env bash
# IdleHunter - Setup a Linux host with Docker and Docker Compose
# Run ON the server (e.g. Ubuntu 22.04/24.04, Debian).
# Usage: bash scripts/setup-host.sh
# Or from your machine: ssh user@your-server 'bash -s' < scripts/setup-host.sh

set -e

echo "=== IdleHunter: Setting up host for Docker ==="

if command -v docker &>/dev/null && docker compose version &>/dev/null 2>/dev/null; then
  echo "Docker and Docker Compose already installed."
  docker --version
  docker compose version
  exit 0
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y apt-transport-https ca-certificates curl

# Remove conflicting packages (Ubuntu may ship docker.io)
apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Docker official repo (Ubuntu 22.04/24.04; for other distros see https://docs.docker.com/engine/install/)
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "${VERSION_CODENAME:-noble}") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

systemctl enable docker
systemctl start docker

echo "=== Done. Docker and Docker Compose are installed ==="
docker --version
docker compose version

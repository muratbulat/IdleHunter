# IdleHunter — Deployment Guide

This guide covers deploying IdleHunter to any host that supports **Docker** and **Docker Compose** (e.g. a VPS, cloud VM, or any Linux server).

---

## Prerequisites on the host

- **Docker** 24+ and **Docker Compose** v2 (or `docker-compose` v2)
- Outbound network access (for LDAP, vCenter, Aria, Stor2RRD, SMTP if used)
- Recommended: 2+ CPU cores, 4 GB RAM (scale up for ~1500 VMs)

---

## 1. Deploy on the server (run on the host)

Use this when you are already on the server (e.g. via SSH) and the project is at `/path/to/IdleHunter`.

### 1.1 Get the code on the server

```bash
# Option A: Clone from Git
git clone https://github.com/muratbulat/IdleHunter.git
cd IdleHunter

# Option B: Upload/copy the project (SCP, SFTP, rsync, etc.)
# Then: cd /path/to/IdleHunter
```

### 1.2 One-time: install Docker (if needed)

On Ubuntu 22.04/24.04:

```bash
cd /path/to/IdleHunter
sudo bash scripts/setup-host.sh
```

Or from your machine: `ssh user@your-server 'bash -s' < scripts/setup-host.sh`

For other distros, see [Docker Engine install](https://docs.docker.com/engine/install/).

### 1.3 Configure environment

```bash
cp .env.example .env
nano .env   # or vim
```

**Required for production:**

- `SECRET_KEY` — long random string (e.g. `python -c "import secrets; print(secrets.token_urlsafe(50))"`).
- `DEBUG=0`
- `ALLOWED_HOSTS` — your public hostname(s) or IP, e.g. `idlehunter.example.com` or `192.168.1.10`.
- `CSRF_TRUSTED_ORIGINS` — e.g. `https://idlehunter.example.com` or `http://192.168.1.10`
- `POSTGRES_PASSWORD` — strong password (keep secret).

### 1.4 Build and run

```bash
./scripts/deploy-on-server.sh
```

Or manually:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### 1.5 First-time setup

```bash
docker compose exec web python manage.py createsuperuser

# Optional: demo data
docker compose exec web python manage.py load_demo_data

# Optional: run idle detection
docker compose exec web python manage.py run_idle_detection
```

### 1.6 App URLs

Open **http://\<server-ip\>:8000** (or your hostname). Get the IP with `hostname -I | awk '{print $1}'`.

| URL | Description |
|-----|-------------|
| `/` | Redirects to dashboard. |
| `/dashboard/` | NOC dashboard (KPIs, charts, VM data grid with search, filters, sort, pagination). |
| `/admin/` | IdleHunter Yönetim (Django admin). |
| `/swagger/` | REST API docs (Swagger UI). |
| `/redoc/` | REST API docs (ReDoc). |
| `/api/health/` | Health check (no auth). |
| `/api/vms/` | VM list API (authenticated). |

---

## 2. Production checklist

Before going live:

| Item | Action |
|------|--------|
| **SECRET_KEY** | Unique, random; never commit. |
| **DEBUG** | Set to `0`. |
| **ALLOWED_HOSTS** | Your public hostname(s) or IP. |
| **CSRF_TRUSTED_ORIGINS** | `https://your-domain` (and http if needed). |
| **POSTGRES_PASSWORD** | Strong; in `.env` or secrets only. |
| **HTTPS** | Use a reverse proxy (Caddy, Nginx) in front of the `web` container. |
| **Backups** | Back up the `postgres_data` volume (and Redis if needed). |
| **Firewall** | Expose only 80/443 (and SSH); do not expose 8000, 5432, 6379 publicly. |

---

## 3. Reverse proxy (recommended)

Run IdleHunter behind a reverse proxy for TLS:

**Caddy** (auto HTTPS):

```text
idlehunter.example.com {
    reverse_proxy localhost:8000
}
```

**Nginx**:

```nginx
server {
    listen 80;
    server_name idlehunter.example.com;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Set `CSRF_TRUSTED_ORIGINS=https://idlehunter.example.com` and `ALLOWED_HOSTS=idlehunter.example.com`.

---

## 4. Updating the app

```bash
cd IdleHunter
git pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml build web celery_worker celery_beat
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Migrations run automatically via the web container entrypoint.

---

## 5. Troubleshooting

- **502 / connection refused** — Check `docker compose ps` and `docker compose logs web`; ensure `web` is listening on 8000.
- **CSRF / 403** — Add your URL to `CSRF_TRUSTED_ORIGINS` and your domain to `ALLOWED_HOSTS`.
- **DB connection errors** — Confirm `POSTGRES_*` or `DATABASE_URL` in `.env`; ensure `db` is healthy before `web` starts.
- **Celery not running** — Check `docker compose logs celery_worker` and `celery_beat`; verify `CELERY_BROKER_URL` and Redis.
- **Broken static files / icons** — Rebuild: `docker compose build --no-cache web && docker compose up -d web`. Then `docker compose exec web python manage.py collectstatic --noinput` and restart the web container if needed.

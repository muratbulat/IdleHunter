# IdleHunter

**IdleHunter** is an open-source web application that **detects idle/zombie virtual machines (VMs)** across VMware vCenter, VMware Aria, and Stor2RRD. It uses rule-based detection (and is designed for future ML-based scoring) to flag VMs with no activity, so you can reclaim resources and clean up your estate.

---

## Features

| Feature | Description |
|--------|-------------|
| **Idle detection** | Rule-based: VMs with no activity for N days (default 7) are marked idle. `idle_score` 0.0 = active, 1.0 = idle. Resource-based scoring (CPU/network/disk) for powered-on VMs. |
| **Data sources** | vCenter 8.x, VMware Aria, Stor2RRD. Add sources in Admin; Celery tasks fetch VMs and run detection after each scan. |
| **Dashboard** | NOC-style dark UI: KPI cards, donut/bar charts, **VM data grid** with search, filters (Tümü / Zombi / Aktif / Kapalı), **sortable columns** (Ad, Kaynak, Güç, Puan), pagination (20 per page). Default sort: idle score descending. |
| **REST API & Swagger** | REST API for health, VM list/detail, data sources. **Swagger UI** at `/swagger/`, ReDoc at `/redoc/`. Session auth for protected endpoints. |
| **Scheduled scans** | Celery Beat runs daily scans; optional per-source scans. |
| **Auth & RBAC** | Django auth, optional LDAP, optional MFA; roles (Viewer/Operator/Admin) via `apps.accounts`. |
| **i18n** | Turkish (default) and English; gettext in `locale/`. |

---

## Quick start (Docker)

```bash
git clone https://github.com/muratbulat/IdleHunter.git
cd IdleHunter
cp .env.example .env
# Edit .env: SECRET_KEY, POSTGRES_PASSWORD, ALLOWED_HOSTS
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
# Optional: load demo data
docker compose exec web python manage.py load_demo_data
# Optional: run idle detection on existing VMs
docker compose exec web python manage.py run_idle_detection
```

- **Web UI / Dashboard:** http://localhost:8000 (redirects to `/dashboard/`)  
- **Dashboard:** http://localhost:8000/dashboard/  
- **Admin (IdleHunter Yönetim):** http://localhost:8000/admin/  
- **API docs (Swagger):** http://localhost:8000/swagger/  
- **ReDoc:** http://localhost:8000/redoc/

---

## Directory structure

```
IdleHunter/
├── .env.example
├── .gitignore
├── README.md
├── ROADMAP.md
├── DEPLOYMENT.md
├── CONTRIBUTING.md
├── LICENSE
├── docker-compose.yml
├── docker-compose.prod.yml
├── Dockerfile
├── entrypoint.sh
├── manage.py
├── requirements.txt
├── config/                 # Django project
│   ├── settings/           # base, development, production, docker, ldap
│   ├── urls.py             # Admin, auth, dashboard, api, swagger/redoc
│   ├── views.py            # Home: redirect to /dashboard/
│   ├── api.py              # REST API views (health, vms, data-sources)
│   ├── api_urls.py         # API routes
│   ├── celery.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── core/               # TimeStampedModel, shared base
│   ├── accounts/           # UserProfile, Role, LDAP/MFA, RBAC
│   ├── scans/              # DataSource, VirtualMachine, ScanRun, detection
│   │   ├── detection.py    # Rule-based idle scoring (idle_score)
│   │   ├── tasks.py        # Celery: fetch VMs, run_scan, run_detection
│   │   └── management/commands/
│   │       ├── load_demo_data.py
│   │       └── run_idle_detection.py
│   ├── web/                # Dashboard app (NOC UI, data grid)
│   │   ├── views.py        # Dashboard view (KPIs, charts, paginated VM list)
│   │   ├── urls.py
│   │   └── templatetags/   # dashboard_extras (get_item filter)
│   └── integrations/      # vCenter, Aria, Stor2RRD API clients
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── dashboard/          # NOC dashboard (index.html)
│   └── registration/
├── locale/
│   ├── tr/LC_MESSAGES/
│   └── en/LC_MESSAGES/
└── scripts/
    ├── deploy-on-server.sh   # Run on the host to build and start the stack
    └── setup-host.sh         # One-time: install Docker on Ubuntu 22.04/24.04
```

---

## Configuration

See `.env.example`. Important variables:

- **Django:** `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`
- **Database:** `POSTGRES_*` or `DATABASE_URL`
- **Redis/Celery:** `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`
- **Idle detection:** `IDLE_DAYS_THRESHOLD` (default `7`) — days without activity to consider a VM idle
- **Optional:** LDAP (`LDAP_*`), MFA (`ENABLE_MFA`), vCenter/Aria/Stor2RRD, SMTP

---

## REST API

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/health/` | GET | No | Health check. |
| `/api/vms/` | GET | Yes | Paginated VM list; query params: `q`, `status` (all \| zombie \| active \| powered_off), `page`. |
| `/api/vms/<id>/` | GET | Yes | Single VM by ID. |
| `/api/data-sources/` | GET | Yes | List enabled data sources. |

- **Swagger UI:** `/swagger/` — interactive API docs; use session auth (log in to the site first).  
- **ReDoc:** `/redoc/`  
- **OpenAPI schema:** `/swagger.json`, `/swagger.yaml`

---

## Management commands

| Command | Description |
|---------|-------------|
| `load_demo_data` | Create demo DataSources, VMs, and ScanRuns. Use `--clear` to remove demo data only. |
| `run_idle_detection` | Compute `idle_score` for all VMs (e.g. after loading data or for backfill). |
| `migrate` | Apply DB migrations (also run automatically in container entrypoint). |
| `createsuperuser` | Create an admin user. |
| `compilemessages` | Compile locale `.po` to `.mo` (requires gettext; optional in Docker). |

---

## Deployment

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for:

- Deploy on the host: get code, configure `.env`, run `scripts/deploy-on-server.sh`
- Production checklist, reverse proxy, troubleshooting

Production run:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

---

## Roadmap

See **[ROADMAP.md](ROADMAP.md)**. Current state:

- **Steps 1–4:** Base, DB/i18n, LDAP/MFA/RBAC, Celery + vCenter/Aria/Stor2RRD integrations.
- **Step 5 (partial):** Rule-based idle detection; ML scoring planned.
- **Step 6 (partial):** NOC dashboard with data grid, charts, Swagger API; further exports/UI planned.

---

## Contributing

See **[CONTRIBUTING.md](CONTRIBUTING.md)**. Contributions are welcome (issues, PRs, new languages).

---

## Developer

**Murat Bulat**

---

## License

**[MIT License](LICENSE)** — see [LICENSE](LICENSE).

---

*IdleHunter — Detect idle VMs, reclaim resources.*

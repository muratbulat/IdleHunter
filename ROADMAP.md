# IdleHunter — Step-by-Step Implementation Roadmap

This document is a **module-by-module roadmap** to build IdleHunter. Each step is self-contained and can be implemented in order.

**Current status (v0.1.0):** Steps 1–4 done; Step 5 partially done (rule-based idle detection; ML scoring planned); Step 6 (richer UI) planned.

---

## Overview

| Step | Focus | Deliverables |
|------|--------|--------------|
| **Step 1** | Base setup | Dockerfile, docker-compose.yml, Django skeleton, config split |
| **Step 2** | DB & i18n models | PostgreSQL, core models, locale structure, gettext setup |
| **Step 3** | LDAP / MFA & RBAC | Authentication, roles, permissions, MFA |
| **Step 4** | Celery + API integrations | Redis, Celery tasks, vCenter/Aria/Stor2RRD clients |
| **Step 5** | ML engine | Rule-based + scikit-learn idle scoring |
| **Step 6** | UI | Dashboards, charts, datatables, exports, language switcher |

---

## Step 1: Base Setup — Dockerfile & docker-compose.yml

**Goal:** Run a minimal Django app in Docker with all five services (web, db, redis, celery_worker, celery_beat).

**Tasks:**

1. **Create `Dockerfile`**
   - Multi-stage optional: builder for static assets, final stage with Python 3.12, Django, Gunicorn.
   - Use `requirements.txt`; set `WORKDIR`, `ENV PYTHONUNBUFFERED=1`.
   - Default `CMD`: Gunicorn binding to `0.0.0.0:8000`.

2. **Create `docker-compose.yml`**
   - **db:** `postgres:16-alpine`, env from `.env`, volume for data, healthcheck.
   - **redis:** `redis:7-alpine`, optional persistence volume.
   - **web:** Build from `Dockerfile`, depends_on db & redis, env from `.env`, port 8000:8000, volume for code (dev) or none (prod).
   - **celery_worker:** Same image as web, command `celery -A config worker -l info`, depends_on db, redis, web.
   - **celery_beat:** Same image, command `celery -A config beat -l info`, depends_on db, redis, web.

3. **Create Django project skeleton**
   - `config/` as project package: `settings/` (base, development, production, docker), `urls.py`, `wsgi.py`, `asgi.py`.
   - Use `django-environ` in settings for `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DATABASE_URL`, `REDIS_URL`, `CELERY_BROKER_URL`.

4. **Create `.env.example`**
   - Placeholders for: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `POSTGRES_*`, `REDIS_URL`, `CELERY_BROKER_URL`, (optional) `CSRF_TRUSTED_ORIGINS`.

5. **Create `.gitignore`**
   - Python, Django, Docker, IDE, `.env` (never commit secrets).

**Acceptance:** `docker-compose up --build` brings up web; http://localhost:8000 shows a simple Django page (e.g. "IdleHunter" or 404 with DEBUG).

---

## Step 2: DB & i18n Models

**Goal:** PostgreSQL as default DB, core app with shared models, and full i18n (gettext, default Turkish, English).

**Tasks:**

1. **Database**
   - In `config/settings/base.py`: use `dj-database-url` or `django-environ` for `DATABASES['default']` from `DATABASE_URL` (PostgreSQL).
   - Ensure migrations run on first `docker-compose up` or document `migrate` in README.

2. **Apps structure**
   - Create `apps/` package; add `core` app (e.g. `apps/core`).
   - In `core`: base models (e.g. `TimeStampedModel`), mixins, shared helpers. Register in `INSTALLED_APPS`.

3. **Domain models (minimal for Step 2)**
   - In `apps/core` or a new `apps/scans`: models such as `DataSource` (vCenter/Aria/Stor2RRD), `VirtualMachine` (name, uuid, last_seen, data_source FK), `ScanRun` (started_at, finished_at, status). Create and run migrations.

4. **i18n**
   - In settings: `LANGUAGE_CODE = 'tr'`, `LANGUAGES = [('tr', 'Turkish'), ('en', 'English')]`, `LOCALE_PATHS = [BASE_DIR / 'locale']`.
   - Create `locale/tr/LC_MESSAGES` and `locale/en/LC_MESSAGES`; add `django.po` (can be empty or with a few keys).
   - In `config/urls.py`: add `i18n_patterns` for URL prefix (e.g. `/tr/`, `/en/`) and set `prefix_default_language=False` or True per preference.
   - Add middleware: `django.middleware.locale.LocaleMiddleware`.
   - Document: `makemessages -l en -l tr` and `compilemessages` in README/scripts.

**Acceptance:** Migrations apply; Django admin (or a minimal view) shows core models; switching URL between `/tr/` and `/en/` works; `compilemessages` runs without error.

---

## Step 3: LDAP / MFA & RBAC

**Goal:** Users authenticate via LDAP/AD; optional MFA; Role-Based Access Control for IdleHunter features.

**Tasks:**

1. **LDAP**
   - Install and configure `django-auth-ldap`. In settings (or a dedicated `auth.py`): `AUTH_LDAP_SERVER_URI`, `AUTH_LDAP_BIND_DN`, `AUTH_LDAP_BIND_PASSWORD`, `AUTH_LDAP_USER_SEARCH`, user/group mapping. Use env vars for all secrets.
   - `AUTHENTICATION_BACKENDS`: include `django_auth_ldap.backend.LDAPBackend` and `django.contrib.auth.backends.ModelBackend` (for superuser/local).

2. **User model**
   - If extending: custom User model in `apps/accounts` (e.g. profile, role FK). Otherwise use Django User + Profile with Role. Create `Role` and `UserRole` (or Permission groups). Run migrations.

3. **RBAC**
   - Define permission sets: e.g. View Dashboard, Run Scan, Manage Data Sources, Manage Users. Use Django groups or custom `Role` with permissions. Middleware or view decorators to enforce.

4. **MFA**
   - Integrate `django-mfa2` (or chosen library): register in `INSTALLED_APPS`, URLs, required MFA for sensitive views. Document enable/disable via setting.

5. **Login / Logout**
   - Login page (and optional language switcher); logout; redirect after login to dashboard (Step 6). Protect all IdleHunter views with login and RBAC checks.

**Acceptance:** Login with LDAP; optional MFA; role-based access to placeholder dashboard and admin; no secrets in repo.

---

## Step 4: Celery + API Integrations

**Goal:** Celery worker and beat run; tasks call vCenter 8.0.3, VMware Aria, and Stor2RRD APIs; results cached in Redis and stored in DB.

**Tasks:**

1. **Celery app**
   - In `config/`: `celery.py` defining app with `broker_url`, `result_backend`, timezone, `beat_schedule` (placeholder). In `config/__init__.py`: `from .celery import app as celery_app`.

2. **Django integration**
   - Install `django-celery-results` and `django-celery-beat`; store results in DB or Redis; use `DatabaseScheduler` for beat. Create Celery beat migrations.

3. **API clients (in `apps/integrations`)**
   - **vCenter:** Use `pyvmomi`; connection helper (host, user, password, port); function to list VMs (name, uuid, power state, basic metrics). Wrap in try/except and timeouts.
   - **VMware Aria:** REST client (requests) for metrics relevant to idle (CPU, memory, disk I/O). Document required Aria API version and endpoints.
   - **Stor2RRD:** REST or file-based client per Stor2RRD docs; fetch storage I/O or similar for VMs. Abstract behind a common interface (e.g. `get_vm_metrics(vm_id)`).

4. **Tasks**
   - Task `fetch_vcenter_vms(data_source_id)` → update or create `VirtualMachine` and raw metric cache (Redis or DB).
   - Similar tasks for Aria and Stor2RRD; optionally one orchestration task that runs all three and marks a `ScanRun`.
   - Use Redis for short-lived cache (e.g. API response cache) to avoid re-hitting APIs on every run.

5. **Scheduled scan**
   - In Celery beat schedule: run the orchestration task on a cron (e.g. daily). Configurable via env or Django admin later.

**Acceptance:** `docker-compose up` runs worker and beat; tasks execute without error with mock or real credentials; VM list (or mock data) appears in DB; Redis used for caching.

---

## Step 5: ML Engine (Rule-Based + Anomaly Detection)

**Goal:** Compute an "Idle Confidence Score" per VM using rules and scikit-learn anomaly detection.

**Tasks:**

1. **Rule-based component**
   - In `apps/engine`: define rules (e.g. CPU < 5%, memory < 10%, no disk I/O for N days, powered off for X days). Each rule returns a partial score or boolean. Combine into a rule-based score (e.g. 0–100).

2. **Feature set**
   - From DB/Redis: per-VM metrics (CPU, memory, disk I/O, power state, uptime). Build a small feature matrix (pandas DataFrame) for the last N days per VM.

3. **Anomaly detection**
   - Use scikit-learn (e.g. `IsolationForest` or `LocalOutlierFactor`) on the feature matrix to label "idle-like" VMs. Map output to a 0–100 score (e.g. via decision_function or threshold).

4. **Hybrid score**
   - Combine rule-based and ML scores (e.g. weighted average or max). Store in `VirtualMachine` or a `VMIdleScore` model (vm FK, score, rule_score, ml_score, computed_at).

5. **Celery task**
   - Task `compute_idle_scores(scan_run_id)` loads VMs and metrics, runs rules + ML, saves scores. Triggered after `fetch_*` tasks in the orchestration from Step 4.

**Acceptance:** Running the pipeline produces per-VM Idle Confidence Score; scores are persisted and viewable (e.g. in admin or a simple API).

---

## Step 6: UI — Dashboards, Charts, Exports, Language Switcher

**Goal:** Interactive dashboards, charts (total VMs, reclaimable resources, idle scores), exportable datatables (CSV/PDF), and language switcher.

**Tasks:**

1. **Templates & static**
   - Base template (Bootstrap 5 or Tailwind); blocks for content and scripts. Include Chart.js or ApexCharts from CDN or static.

2. **Dashboard view**
   - View (and URL) for main dashboard: total VMs, count by idle score band (e.g. high/medium/low), reclaimable resources (sum of CPU/RAM for high-idle VMs). Data from DB; use caching if needed.

3. **Charts**
   - At least: total VMs over time or by cluster; reclaimable CPU/RAM; distribution of Idle Confidence Scores (e.g. bar or pie). Use Chart.js or ApexCharts with data from the same view or a small JSON API.

4. **Data table**
   - Table of VMs with columns: name, cluster, idle score, CPU, memory, power state, last seen. Server-side or client-side pagination; sortable/filterable (e.g. Django tables2 or simple HTMX or vanilla JS).

5. **Exports**
   - CSV: same dataset as table (Django HttpResponse with csv writer or pandas to_csv).
   - PDF: use WeasyPrint or ReportLab; table or summary report. Button or link "Export PDF" / "Export CSV" on dashboard or VM list.

6. **Language switcher**
   - In base template: dropdown or links to switch current URL to another language (e.g. `/en/...` ↔ `/tr/...`). Use `request.LANGUAGE_CODE` and `i18n_patterns`; ensure all dashboard strings are in `.po` files.

7. **Alerts / scheduled reports (optional for Step 6)**
   - Celery task: build summary (e.g. top 20 idle VMs, reclaimable totals) and send email via SMTP (Django email backend). Schedule with Celery Beat. Document SMTP env vars.

**Acceptance:** Dashboard loads with charts and table; CSV and PDF export work; switching language updates UI; scheduled email report sends (if implemented).

---

## After the Roadmap

- **Security review:** Secrets, CSRF, CORS, rate limiting, LDAP bind credentials.
- **Documentation:** API docs (e.g. drf-spectacular if using DRF), operator runbook, contribution guide.
- **CI/CD:** GitHub Actions for tests, lint, and optional Docker build.
- **Release:** Tag v0.1.0, publish to GitHub, add license (e.g. MIT).

---

When you are ready, say **"Begin Step 1"** (or the step you want to start with), and we will implement it in detail in the repository.

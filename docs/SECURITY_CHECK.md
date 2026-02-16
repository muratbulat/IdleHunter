# Security check (before publishing to GitHub)

Before pushing, ensure **no** real credentials or secrets are in the repo.

## Checklist

- [ ] **`.env`** — Must be in `.gitignore` and never committed. Only `.env.example` (placeholders) is in the repo.
- [ ] **Passwords / secrets** — No real `SECRET_KEY`, `POSTGRES_PASSWORD`, `VCENTER_PASSWORD`, `ARIA_TOKEN`, `LDAP_BIND_PASSWORD`, API keys, or tokens in tracked files.
- [ ] **IP addresses** — No real server IPs (e.g. `10.48.x.x`) in code or docs; use placeholders like `192.168.1.10` or `your-server-ip`.
- [ ] **Usernames / emails** — No real personal emails or login names; only examples like `administrator@vsphere.local`, `idlehunter@example.com`.
- [ ] **SSH keys / certs** — No `.pem`, `*.key`, or private key files; they are in `.gitignore`.

## What is safe in the repo

- **`.env.example`** — Placeholder values only (`your-secret-key-change-in-production`, `change-me`, `localhost`, `example.com`).
- **Docs** — `DEPLOYMENT.md`, `README.md` use generic examples (e.g. `192.168.1.10`, `idlehunter.example.com`).
- **Demo data** — `load_demo_data.py` uses `vcenter-demo.example.com`, `aria-demo.example.com` and env keys for passwords.

## If you accidentally committed secrets

1. Rotate the secret immediately (new password, new key, new token).
2. Remove the secret from git history (e.g. `git filter-branch` or BFG Repo-Cleaner) or create a new repo and force-push.
3. Never rely on “we’ll remove it in the next commit” — history stays visible.

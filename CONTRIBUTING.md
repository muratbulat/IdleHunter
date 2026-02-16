# Contributing to IdleHunter

Thank you for considering contributing to IdleHunter.

## How to contribute

1. **Fork** the repository on GitHub.
2. **Clone** your fork and create a branch (e.g. `feature/my-feature` or `fix/issue-123`).
3. **Make your changes** — keep the code style consistent (e.g. Black for Python if adopted).
4. **Test** locally (Docker: `docker compose up`, run migrations, smoke-test the UI).
5. **Commit** with clear messages (e.g. "Add IDLE_DAYS_THRESHOLD to .env.example").
6. **Push** to your fork and open a **Pull Request** against the default branch.

## What we welcome

- **Bug reports** — open an issue with steps to reproduce and environment details.
- **Feature ideas** — open an issue to discuss before large PRs.
- **Code** — fixes, new features (especially aligned with [ROADMAP.md](ROADMAP.md)).
- **Translations** — new or improved `.po` files in `locale/` (run `makemessages` / `compilemessages` as needed).
- **Documentation** — fixes and improvements to README, DEPLOYMENT, ROADMAP.

## Development setup

- Python 3.12+, Django 5.x, PostgreSQL 16, Redis 7.
- Use `.env.example` as base; set `DEBUG=1` and `ALLOWED_HOSTS=localhost,127.0.0.1` for local run.
- Run with Docker: `docker compose up -d` then `docker compose exec web python manage.py migrate` and `load_demo_data` if you want demo data.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).

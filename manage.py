#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

# Ensure project root (directory containing manage.py) is on sys.path first,
# so that "apps" and "config" packages are found when running in Docker etc.
_project_root = Path(__file__).resolve().parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


def main():
    """Run administrative tasks."""
    if not (_project_root / "apps").is_dir():
        sys.stderr.write(
            f"Error: Project root {_project_root} has no 'apps' directory. "
            "Ensure the full IdleHunter project (including apps/) is present before building the Docker image.\n"
        )
        sys.exit(1)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

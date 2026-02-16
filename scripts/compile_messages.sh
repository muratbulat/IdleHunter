#!/usr/bin/env bash
# Compile gettext .po files to .mo (run from project root, with Django env active)
set -e
cd "$(dirname "$0")/.."
python manage.py compilemessages -i env

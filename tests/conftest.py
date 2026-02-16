# Pytest fixtures and config for IdleHunter
import os

import pytest


def pytest_configure(config):
    """Use development settings (SQLite) when no DJANGO_SETTINGS_MODULE is set."""
    if not os.environ.get("DJANGO_SETTINGS_MODULE"):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")


@pytest.fixture
def client(db):
    """Django test client (db fixture from pytest-django)."""
    from django.test import Client
    return Client()

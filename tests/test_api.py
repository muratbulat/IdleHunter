# Tests for config.api (REST API)
import pytest


def test_api_health_allow_any(client):
    """Health endpoint is public and returns ok."""
    response = client.get("/api/health/")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"
    assert data.get("service") == "IdleHunter"


@pytest.mark.django_db
def test_api_vm_list_requires_auth(client):
    """VM list endpoint requires authentication."""
    response = client.get("/api/vms/")
    assert response.status_code in (401, 403)

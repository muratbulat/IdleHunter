# Tests for config.views (home redirect)
import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_home_redirects_to_dashboard(client):
    """Anonymous user hitting / is redirected to login, then after login to dashboard."""
    response = client.get(reverse("home"), follow=False)
    # home is login_required, so redirect to login
    assert response.status_code == 302
    assert "login" in response["Location"]


@pytest.mark.django_db
def test_home_redirects_to_dashboard_when_authenticated(client, django_user_model):
    """Authenticated user hitting / is redirected to dashboard."""
    user = django_user_model.objects.create_user(username="testuser", password="testpass123")
    client.force_login(user)
    response = client.get(reverse("home"), follow=False)
    assert response.status_code == 302
    assert response["Location"].endswith(reverse("web:dashboard"))

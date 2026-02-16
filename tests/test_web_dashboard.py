# Tests for apps.web.views (dashboard)
import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_dashboard_requires_login(client):
    """Dashboard redirects anonymous users to login."""
    response = client.get(reverse("web:dashboard"), follow=False)
    assert response.status_code == 302
    assert "login" in response["Location"]


@pytest.mark.django_db
def test_dashboard_200_when_authenticated(client, django_user_model):
    """Dashboard returns 200 for authenticated user."""
    user = django_user_model.objects.create_user(username="testuser", password="testpass123")
    client.force_login(user)
    response = client.get(reverse("web:dashboard"))
    assert response.status_code == 200

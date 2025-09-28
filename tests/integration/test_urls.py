import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
def test_api_root():
    """
    Test that API root endpoint returns basic information.
    """
    client = Client()
    url = reverse("api-root")
    resp = client.get(url)
    assert resp.status_code == 200
    data = resp.json()
    assert "endpoints" in data
    assert "message" in data
    assert data["message"] == "Savannah Assess API"


@pytest.mark.django_db
def test_api_landing_authenticated():
    """
    Test that API landing page works for authenticated users.
    """
    # Create a user and login
    user = User.objects.create_user(username="testuser", email="test@example.com", password="password123")
    client = Client()
    assert client.login(username="testuser", password="password123"), "Login failed"

    url = reverse("api-landing")
    resp = client.get(url)

    # Authenticated users should get 200
    assert resp.status_code == 200, f"Unexpected response: {resp.status_code} - {resp.content}"

    data = resp.json()
    assert data["authenticated"] is True
    assert data["message"] == "Welcome to Savannah Assess API"
    assert "user" in data
    assert data["user"]["username"] == user.username
    assert data["user"]["email"] == user.email


@pytest.mark.django_db
def test_api_landing_redirects_unauthenticated():
    """
    Test that API landing page redirects unauthenticated users to OIDC login.
    """
    client = Client()
    url = reverse("api-landing")
    resp = client.get(url)

    # Unauthenticated users should be redirected to login
    assert resp.status_code == 302
    assert "/oidc/authenticate/" in resp.url

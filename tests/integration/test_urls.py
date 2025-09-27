# tests/integration/test_urls.py
import pytest
from django.urls import reverse

from tests.factories.factories import UserFactory 


@pytest.mark.django_db
def test_api_root(client):
    url = reverse("api-root")
    resp = client.get(url)
    assert resp.status_code == 200
    assert "endpoints" in resp.json()


@pytest.mark.django_db
def test_api_landing_requires_login(client):
    user = UserFactory()
    client.force_login(user)
    url = reverse("api-landing")
    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.json()["authenticated"] is True

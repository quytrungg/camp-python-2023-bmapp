from django.test import Client
from django.urls import reverse


def test_homepage_view(auth_client: Client) -> None:
    """Ensure homepage view responses with status code 200."""
    response = auth_client.get(reverse("home"))

    assert response.status_code == 200

from django.urls import reverse

from rest_framework.test import APIClient


def test_homepage_api(api_client: APIClient) -> None:
    """Ensure homepage api responses with status code 200 and has data."""
    response = api_client.get(reverse("v1:home"))

    assert response.status_code == 200
    assert response.data

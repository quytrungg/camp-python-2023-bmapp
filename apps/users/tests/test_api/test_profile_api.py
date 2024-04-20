from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient


def test_profile_api(api_client: APIClient) -> None:
    """Ensure authenticated user can access API with status code 200."""
    response = api_client.get(reverse("v1:profile"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data


def test_profile_api_unauthenticated() -> None:
    """Restrict unauthenticated users from API with status code 401."""
    response = APIClient().get(reverse("v1:profile"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

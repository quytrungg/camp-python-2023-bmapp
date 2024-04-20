from rest_framework.test import APIClient

import pytest

from apps.users.models import User


@pytest.fixture(scope="session")
def api_client(normal_user: User) -> APIClient:
    """Create api client."""
    client = APIClient()
    client.force_authenticate(user=normal_user)
    return client


@pytest.fixture(scope="session")
def another_api_client(another_user: User) -> APIClient:
    """Create api client."""
    client = APIClient()
    client.force_authenticate(user=another_user)
    return client

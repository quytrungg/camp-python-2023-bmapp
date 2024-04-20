"""Configuration file for pytest."""
from django.test import Client

import pytest

from apps.users.models import User


@pytest.fixture
def from_user(normal_user: User) -> User:
    """Alias the normal_user fixture."""
    return normal_user


@pytest.fixture
def to_user(another_user: User) -> User:
    """Alias the another_user fixture."""
    return another_user


@pytest.fixture
def from_client(from_user: User) -> Client:
    """Return from_user client fixture."""
    client = Client()
    client.force_login(from_user)
    return client


@pytest.fixture
def to_client(to_user: User) -> Client:
    """Return to_user client fixture."""
    client = Client()
    client.force_login(to_user)
    return client

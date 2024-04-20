from typing import Any

from django.test import Client
from django.urls import reverse

import pytest

from apps.users.models import User


@pytest.fixture
def register_url() -> str:
    """Return the URL of the register page."""
    return reverse("register")


@pytest.fixture
def valid_user_data() -> dict[str, Any]:
    """Return a valid user data for registration."""
    return {
        "username": "testuser",
        "password1": "P@55w0rd",
        "password2": "P@55w0rd",
        "email": "testuser@gmail.com",
        "phone_number": "+84987654321",
    }


def test_user_register_success(
    client: Client,
    register_url: str,
    valid_user_data: dict[str, Any],
) -> None:
    """Ensure that the user with valid data can register successfully."""
    response = client.post(register_url, valid_user_data)
    assert response.status_code == 302  # Check if redirected
    assert User.objects.filter(
        username=valid_user_data["username"],
        email=valid_user_data["email"],
        phone_number=valid_user_data["phone_number"],
    ).exists()


def test_user_register_with_duplicated_data(
    normal_user: User,
    client: Client,
    register_url: str,
) -> None:
    """Ensure that the user cannot register with duplicated data."""
    user_data = {
        "username": normal_user.username,
        "password1": "P@55w0rd",
        "password2": "P@55w0rd",
        "email": normal_user.email,
        "phone_number": normal_user.phone_number,
    }
    client.post(register_url, user_data)
    assert User.objects.filter(
        username=user_data["username"],
        email=user_data["email"],
        phone_number=user_data["phone_number"],
    ).count() == 1


@pytest.mark.parametrize(
    "invalid_user_data",
    [
        {
            "username": "testuser",
            "password1": "1234",
            "password2": "1234",
            "email": "testuser@gmail.com",
            "phone_number": "+84987654321",
        },
        {
            "username": "testuser",
            "password1": "12345678",
            "password2": "12345678",
            "email": "testuser@gmail.com",
            "phone_number": "+84987654321",
        },
        {
            "username": "testuser",
            "password1": "testuser",
            "password2": "testuser",
            "email": "testuser@gmail.com",
            "phone_number": "+84987654321",
        },
        {
            "username": "testuser",
            "password1": "P@55w0rd",
            "password2": "P@55w0rd",
            "email": "testuser",
            "phone_number": "+84987654321",
        },
        {
            "username": "testuser",
            "password1": "P@55w0rd",
            "password2": "P@5555w0rd",
            "email": "testuser@test.com",
            "phone_number": "+84987654321",
        },
        {
            "username": "testuser",
            "password1": "P@55w0rd",
            "password2": "P@55w0rd",
            "email": "testuser",
            "phone_number": "+849876543211111",
        },
    ],
)
def test_user_register_fail(
    client: Client,
    register_url: str,
    invalid_user_data: dict[str, Any],
) -> None:
    """Ensure that the user cannot register with invalid data."""
    client.post(register_url, invalid_user_data)
    assert not User.objects.filter(
        username=invalid_user_data["username"],
        email=invalid_user_data["email"],
        phone_number=invalid_user_data["phone_number"],
    ).exists()

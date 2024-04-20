from typing import Any

from django.test import Client
from django.urls import reverse

import pytest

from apps.rates.models import Currency
from apps.users.models import User


@pytest.fixture
def first_update_valid_data(first_currency: Currency) -> dict[str, Any]:
    """Provide a valid data for the UserFirstUpdateView."""
    return {
        "first_name": "Test",
        "last_name": "User",
        "date_of_birth": "1990-01-01",
        "default_currency": first_currency.pk,
    }


def test_first_update_view(
    auth_client: Client,
    normal_user: User,
    first_update_valid_data: dict[str, Any],
) -> None:
    """Ensure that the view works for the correct user.

    Date of birth and default currency are selected from widget/dropdown,
        so there is no need to test for cases
        that user input invalid dob/currency.

    """
    url = reverse("first-time-update")
    response = auth_client.post(url, first_update_valid_data)

    assert response.status_code == 302

    normal_user.refresh_from_db()
    assert normal_user.updated_information is True

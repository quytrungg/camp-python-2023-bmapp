from decimal import Decimal
from typing import Any

from django.test import Client
from django.urls import reverse

import pytest

from apps.rates.factories import ExchangeRateFactory
from apps.rates.models import ExchangeRate
from apps.users.models import User


@pytest.fixture
def reverse_exchange_rate(
    exchange_rate_valid_data: dict[str, Any],
    normal_user: User,
) -> ExchangeRate:
    """Create a mock reverse exchange rate."""
    return ExchangeRateFactory(
        user=normal_user,
        source_currency_id=exchange_rate_valid_data["destination_currency"],
        destination_currency_id=exchange_rate_valid_data["source_currency"],
        rate=Decimal(1 / exchange_rate_valid_data["rate"]),
    )


@pytest.fixture
def rate_update_data() -> dict[str, Any]:
    """Return valid data for updating an exchange rate."""
    return {"rate": Decimal(2)}


def test_rate_update_view(
    auth_client: Client,
    exchange_rate: ExchangeRate,
    reverse_exchange_rate: ExchangeRate,
    rate_update_data: dict[str, Any],
):
    """Ensure that a user can update their own exchange rate.

    There is no need to check for positive exchange rate constraint,
    because it will be tested in the front-end side.

    """
    url = reverse("rate-update", kwargs={"pk": exchange_rate.pk})
    response = auth_client.post(url, rate_update_data)
    assert response.status_code == 302
    exchange_rate.refresh_from_db()

    assert exchange_rate.rate == rate_update_data["rate"]


def test_not_own_rate_update_view(
    exchange_rate: ExchangeRate,
    rate_update_data: dict[str, Any],
    another_client: Client,
):
    """Ensure that a user cannot update another user's exchange rate."""
    url = reverse("rate-update", kwargs={"pk": exchange_rate.pk})
    response = another_client.post(url, rate_update_data)

    assert response.status_code == 404

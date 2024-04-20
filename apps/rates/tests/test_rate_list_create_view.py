from decimal import Decimal
from typing import Any

from django.test import Client
from django.urls import reverse

import pytest
from pytest_lazyfixture import lazy_fixture

from apps.rates.models import ExchangeRate
from apps.users.models import User


def test_exchange_rate_list_view(
    auth_client: Client,
) -> None:
    """Ensure that the exchange rate list view works for authenticated user."""
    url = reverse("rate-list")
    response = auth_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db()
def test_valid_data(
    normal_user: User,
    auth_client: Client,
    exchange_rate_valid_data: dict[str, Any],
) -> None:
    """Ensure that the exchange rate create view actually creates a rate.

    The last assert to make sure that a reverse exchange rate is created
        automatically. We don't check the rate because of precision issues.

    """
    url = reverse("rate-create")
    response = auth_client.post(url, exchange_rate_valid_data)
    assert response.status_code == 302
    assert ExchangeRate.objects.filter(
        source_currency=exchange_rate_valid_data["source_currency"],
        destination_currency=exchange_rate_valid_data["destination_currency"],
        rate=exchange_rate_valid_data["rate"],
        user=normal_user,
    ).exists()
    assert ExchangeRate.objects.filter(
        source_currency=exchange_rate_valid_data["destination_currency"],
        destination_currency=exchange_rate_valid_data["source_currency"],
        user=normal_user,
    )


@pytest.mark.django_db()
@pytest.mark.parametrize(
    "invalid_data",
    [
        {
            "source_currency": lazy_fixture("first_currency"),
            "destination_currency": lazy_fixture("first_currency"),
            "rate": Decimal(1),
        },
        {
            "source_currency": lazy_fixture("first_currency"),
            "destination_currency": lazy_fixture("last_currency"),
            "rate": Decimal(1.5),
        },
    ],
)
def test_invalid_data(
    normal_user: User,
    auth_client: Client,
    invalid_data: dict[str, Any],
    exchange_rate: ExchangeRate,
) -> None:
    """Ensure that invalid input cannot be used to create a new rate.

    The first test is to make sure that the source and destination currencies
    are not the same.
    The second test is to make sure that each exchange rate only has one
    instance for a user in the database.

    We don't implement tests for the negative rate because it is handled
    at frontend level.

    """
    invalid_data["source_currency"] = invalid_data["source_currency"]
    invalid_data["destination_currency"] = invalid_data["destination_currency"]
    url = reverse("rate-create")
    response = auth_client.post(url, invalid_data)
    assert response.status_code == 200
    assert ExchangeRate.objects.filter(
        source_currency=exchange_rate.source_currency,
        destination_currency=exchange_rate.destination_currency,
        rate=exchange_rate.rate,
        user=normal_user,
    ).count() == 1

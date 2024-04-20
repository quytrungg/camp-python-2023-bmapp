from decimal import Decimal
from typing import Any

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

import pytest

from apps.rates.factories import ExchangeRateFactory
from apps.rates.models import Currency, ExchangeRate
from apps.users.models import User


@pytest.fixture
def exchange_rate_create_data(
    first_currency: Currency,
    last_currency: Currency,
) -> dict[str, Any]:
    """Provide data for creating an exchange rate."""
    return {
        "source_currency": first_currency.code,
        "destination_currency": last_currency.code,
        "rate": Decimal(1234.5),
    }


@pytest.fixture
def exchange_rate(
    normal_user: User,
    exchange_rate_create_data: dict[str, Any],
) -> ExchangeRate:
    """Create an exchange rate for normal_user."""
    return ExchangeRateFactory(
        user=normal_user,
        source_currency__code=exchange_rate_create_data["source_currency"],
        destination_currency__code=(
            exchange_rate_create_data["destination_currency"]
        ),
    )


def test_exchange_rate_list_api(api_client: APIClient, normal_user) -> None:
    """Ensure that the exchange rate list view returns the correct data."""
    url = reverse("v1:exchange-rate-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == len(
        ExchangeRate.objects.filter(user=normal_user),
    )


def test_exchange_rate_detail_api(
    api_client: APIClient,
    exchange_rate: ExchangeRate,
) -> None:
    """Ensure that a user can see their own exchange rates."""
    url = reverse(
        "v1:exchange-rate-detail",
        kwargs={"pk": exchange_rate.pk},
    )
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data


def test_other_user_exchange_rate_detail_api(
    another_api_client: APIClient,
    exchange_rate: ExchangeRate,
) -> None:
    """Ensure that a user can't see another user's exchange rates."""
    url = reverse(
        "v1:exchange-rate-detail",
        kwargs={"pk": exchange_rate.pk},
    )
    response = another_api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_unauthenticated_user_exchange_rate_list_api() -> None:
    """Ensure that unauthenticated user cannot access the rate list API."""
    url = reverse("v1:exchange-rate-list")
    response = APIClient().get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_unauthenticated_user_exchange_rate_detail_api() -> None:
    """Ensure that unauthenticated user cannot access the rate detail API."""
    url = reverse("v1:exchange-rate-detail", kwargs={"pk": 1})
    response = APIClient().get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_exchange_rate_create_api(
    api_client: APIClient,
    normal_user: User,
    exchange_rate_create_data: dict[str, Any],
) -> None:
    """Ensure that a user can create an exchange rate.

    Also ensure that the reverse exchange rate is created.

    Make sure that the user cannot create the same exchange rate twice.

    """
    url = reverse("v1:exchange-rate-list")
    response = api_client.post(url, data=exchange_rate_create_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert ExchangeRate.objects.filter(
        user=normal_user,
        source_currency__code=exchange_rate_create_data["source_currency"],
        destination_currency__code=(
            exchange_rate_create_data["destination_currency"]
        ),
        rate=exchange_rate_create_data["rate"],
    ).exists()

    # Make sure the reverse exchange rate was created.
    assert ExchangeRate.objects.filter(
        user=normal_user,
        source_currency__code=(
            exchange_rate_create_data["destination_currency"]
        ),
        destination_currency__code=(
            exchange_rate_create_data["source_currency"]
        ),
    ).exists()

    response = api_client.post(url, data=exchange_rate_create_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_not_valid_exchange_rate_create_api(
    api_client: APIClient,
    exchange_rate_create_data: dict[str, Any],
) -> None:
    """Ensure that user cannot create rate with invalid data.

    Invalid data is when source_currency and destination_currency
    are the same.

    """
    exchange_rate_create_data["destination_currency"] = (
        exchange_rate_create_data["source_currency"]
    )
    url = reverse("v1:exchange-rate-list")
    response = api_client.post(url, data=exchange_rate_create_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_exchange_rate_update_api(
    api_client: APIClient,
    exchange_rate_create_data: dict[str, Any],
    exchange_rate: ExchangeRate,
) -> None:
    exchange_rate_create_data["rate"] = Decimal(2345)
    """Ensure that a user can update their own exchange rates.

    The frontend side will handle the limitation of updating
    source and destination currencies.

    """
    url = reverse("v1:exchange-rate-detail", kwargs={"pk": exchange_rate.pk})
    response = api_client.put(url, data=exchange_rate_create_data)

    assert response.status_code == status.HTTP_200_OK
    exchange_rate.refresh_from_db()
    assert exchange_rate.rate == exchange_rate_create_data["rate"]

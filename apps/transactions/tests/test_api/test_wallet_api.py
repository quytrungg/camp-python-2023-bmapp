# pylint: disable=unused-argument
from decimal import Decimal
from typing import Any

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

import pytest

from apps.rates.models import Currency
from apps.transactions.models import Wallet
from apps.users.models import User


@pytest.fixture
def wallet_update_data() -> dict[str, Any]:
    """Return data for updating a wallet."""
    return {
        "name": "Updated Wallet",
        "balance": Decimal(200),
    }


def test_wallet_list_api(
    api_client: APIClient,
    normal_user: User,
    wallets: list[Wallet],
) -> None:
    """Ensure that an authenticated user can access the list API page."""
    url = reverse("v1:wallet-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == Wallet.objects.filter(
        user=normal_user,
    ).count()


def test_wallet_detail_api(
    api_client: APIClient,
    wallet: Wallet,
) -> None:
    """Ensure that an authenticated user can access the detail API page."""
    url = reverse("v1:wallet-detail", kwargs={"pk": wallet.pk})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK


def test_not_owned_wallet_detail(
    another_api_client: APIClient,
    wallet: Wallet,
) -> None:
    """Ensure that a user cannot access the other's wallet detail API page."""
    url = reverse("v1:wallet-detail", kwargs={"pk": wallet.pk})
    response = another_api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_wallet_list_unauthenticated_user() -> None:
    """Ensure that an unauthenticated user cannot access the list API page."""
    url = reverse("v1:wallet-list")
    response = APIClient().get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_wallet_detail_unauthenticated_user(
    wallet: Wallet,
) -> None:
    """Ensure that an unauthenticated user cannot access the detail API."""
    url = reverse("v1:wallet-detail", kwargs={"pk": wallet.pk})
    response = APIClient().get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_wallet_create_api(
    api_client: APIClient,
    normal_user: User,
    wallet_create_data: dict[str, Any],
    first_currency: Currency,
) -> None:
    """Ensure that a user can create a new wallet."""
    normal_user.default_currency = first_currency.code
    url = reverse("v1:wallet-list")
    response = api_client.post(url, data=wallet_create_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert Wallet.objects.filter(
        user=normal_user,
        **wallet_create_data,
    ).exists()


@pytest.mark.parametrize(
    "data",
    [
        {
            "is_premium": True,
            "status_code": status.HTTP_201_CREATED,
        },
        {
            "is_premium": False,
            "status_code": status.HTTP_400_BAD_REQUEST,
        },
    ],
)
def test_max_wallet_create_api(
    api_client: APIClient,
    normal_user: User,
    wallet_create_data: dict[str, Any],
    data: dict[str, Any],
    wallets: list[Wallet],
) -> None:
    """Ensure that the wallet create API works as expected.

    Ensure that a normal user can create up to the limit number of wallets.
    Ensure that a premium user can create as many wallets as they want.

    """
    normal_user.is_premium = data["is_premium"]

    url = reverse("v1:wallet-list")
    response = api_client.post(url, data=wallet_create_data)

    assert response.status_code == data["status_code"]


def test_wallet_update_api(
    api_client: APIClient,
    wallet: Wallet,
    wallet_update_data: dict[str, Any],
) -> None:
    """Ensure that a user can update their wallet.

    As we pop keys which are not allowed to be updated out of the data,
    so we do not need to test the case where the user tries to update
    the currency field.

    """
    url = reverse("v1:wallet-detail", kwargs={"pk": wallet.pk})
    response = api_client.put(url, data=wallet_update_data)

    assert response.status_code == status.HTTP_200_OK
    assert Wallet.objects.filter(
        pk=wallet.pk,
        **wallet_update_data,
    ).exists()


def test_wallet_create_api_without_exchange_rate(
    api_client: APIClient,
    normal_user: User,
    wallet_create_data: dict[str, Any],
) -> None:
    """Ensure that a user cannot create wallet without exchange rate."""
    normal_user.default_currency = Currency.objects.last().code
    url = reverse("v1:wallet-list")
    response = api_client.post(url, data=wallet_create_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

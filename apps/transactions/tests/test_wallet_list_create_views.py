# pylint: disable=unused-argument
from typing import Any

from django.test import Client
from django.urls import reverse

import pytest

from apps.rates.models import Currency
from apps.transactions.constants import NORMAL_USER_LIMITS
from apps.transactions.models import Wallet
from apps.users.models import User


def test_wallet_list_view(
    auth_client: Client,
) -> None:
    """Ensure that the wallet list view returns the correct data."""
    url = reverse("wallet-list")
    response = auth_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db()
def test_wallet_create_view(
    normal_user: User,
    auth_client: Client,
    wallet_create_data: dict[str, Any],
) -> None:
    """Ensure that the wallet create view actually creates a wallet."""
    url = reverse("wallet-create")
    response = auth_client.post(url, wallet_create_data)
    assert response.status_code == 302
    assert Wallet.objects.filter(
        user=normal_user,
        **wallet_create_data,
    ).exists()


@pytest.mark.django_db()
def test_wallet_create_view_max_wallets(
    auth_client: Client,
    normal_user: User,
    wallet_create_data: dict[str, Any],
    wallets: list[Wallet],
) -> None:
    """Ensure that normal user can only create up to the limit.

    The limit is defined in NORMAL_USER_LIMITS["max_wallets_count"] constant.

    """
    url = reverse("wallet-create")
    _ = auth_client.post(url, wallet_create_data, follow=True)
    assert not Wallet.objects.filter(name=wallet_create_data["name"]).exists()
    assert Wallet.objects.filter(
        user=normal_user,
    ).count() == NORMAL_USER_LIMITS["max_wallets_count"]


@pytest.mark.django_db()
def test_wallet_create_view_premium_user(
    auth_client: Client,
    normal_user: User,
    wallet_create_data: dict[str, Any],
) -> None:
    """Ensure that premium user can create more than the limit wallets.

    The limit is defined in NORMAL_USER_LIMITS["max_wallets_count"] constant.

    """
    normal_user.is_premium = True
    normal_user.save()

    # Try to create a new wallet when they reach the limit of
    # NORMAL_USER_LIST["max_wallets_count"] wallets
    url = reverse("wallet-create")
    response = auth_client.post(url, wallet_create_data)
    assert response.status_code == 302
    assert Wallet.objects.filter(
        user=normal_user,
        **wallet_create_data,
    ).exists()


@pytest.mark.django_db()
def test_with_not_exist_exchange_rate(
    auth_client: Client,
    normal_user: User,
    wallet_create_data: dict[str, Any],
    last_currency: Currency,
) -> None:
    """Ensure that an exchange rate must exist."""
    normal_user.default_currency = Currency.objects.get(
        pk=last_currency.pk,
    ).code
    normal_user.save()

    url = reverse("wallet-create")
    response = auth_client.post(url, wallet_create_data)
    assert response.status_code == 200
    assert not Wallet.objects.filter(
        user=normal_user,
        **wallet_create_data,
    ).exists()

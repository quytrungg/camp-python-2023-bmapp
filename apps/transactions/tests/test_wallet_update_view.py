from typing import Any

from django.test import Client
from django.urls import reverse

from apps.transactions.models import Wallet


def test_wallet_update_view(
    auth_client: Client,
    wallet_create_data: dict[str, Any],
    wallet: Wallet,
) -> None:
    """Ensure that the update view of the wallet works.

    The case of negative  balance is not needed to be tested here,
    because it is tested in the front-end side.

    """
    url = reverse("wallet-update", kwargs={"pk": wallet.pk})
    updated_data = wallet_create_data.copy()
    updated_data["balance"] = 200
    response = auth_client.post(url, updated_data)
    wallet.refresh_from_db()

    assert response.status_code == 302
    assert wallet.balance == updated_data["balance"]


def test_not_own_update_view(
    wallet_create_data: dict[str, Any],
    wallet: Wallet,
    another_client: Client,
) -> None:
    """Ensure that a user can only update their own wallets."""
    url = reverse("wallet-update", kwargs={"pk": wallet.pk})
    updated_data = wallet_create_data.copy()
    updated_data["balance"] = 200
    response = another_client.post(url, updated_data)

    assert response.status_code == 404

from django.test import Client
from django.urls import reverse

from apps.transactions.models import Wallet
from apps.users.models import User


def test_wallet_detail_view(
    auth_client: Client,
    wallet: Wallet,
) -> None:
    """Ensure that the wallet detail view works."""
    url = reverse("wallet-detail", kwargs={"pk": wallet.pk})
    response = auth_client.get(url)
    assert response.status_code == 200


def test_not_own_wallet_detail_view(
    wallet: Wallet,
    another_user: User,
) -> None:
    """Ensure that a user cannot see the detail of another user's wallet."""
    client = Client()
    client.force_login(another_user)

    url = reverse("wallet-detail", kwargs={"pk": wallet.pk})
    response = client.get(url)
    assert response.status_code == 404

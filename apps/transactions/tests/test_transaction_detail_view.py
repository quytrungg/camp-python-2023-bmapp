from django.test import Client
from django.urls import reverse

from apps.transactions.models import Transaction
from apps.users.models import User


def test_transaction_detail_view(
    auth_client: Client,
    transaction: Transaction,
) -> None:
    """Ensure Transaction detail page works properly."""
    response = auth_client.get(
        reverse("transaction-detail", kwargs={"pk": transaction.pk}),
    )

    assert response.status_code == 200


def test_transaction_detail_view_invalid(
    transaction: Transaction,
    another_user: User,
) -> None:
    """Ensure user cannot see transaction detail of other users."""
    client = Client()
    client.force_login(another_user)

    response = client.get(
        reverse("transaction-detail", kwargs={"pk": transaction.pk}),
    )
    assert response.status_code == 404

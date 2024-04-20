from django.forms.models import model_to_dict
from django.test import Client
from django.urls import reverse

from apps.transactions.models import Transaction


def test_transaction_delete_view(
    auth_client: Client,
    transaction: Transaction,
) -> None:
    """Ensure Transaction delete page works properly with status code 302."""
    response = auth_client.post(
        reverse("transaction-delete", kwargs={"pk": transaction.pk}),
    )

    assert response.status_code == 302
    assert not Transaction.objects.filter(
        **{
            key: value for key, value in model_to_dict(transaction).items()
            if key not in ["tagged_friends"]
        },
    ).exists()

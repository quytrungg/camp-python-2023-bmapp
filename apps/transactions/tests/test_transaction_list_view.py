from django.test import Client
from django.urls import reverse

from apps.transactions.models import Transaction
from apps.users.models import User


def test_transaction_list_view(auth_client: Client, normal_user: User) -> None:
    """Ensure Transaction list page works properly with status code 200."""
    response = auth_client.get(reverse("transaction-list"))

    assert response.status_code == 200

    response_transaction = response.context_data["transactions"]
    db_transaction = Transaction.objects.filter(
        user=normal_user,
    )[:response.context_data["paginate_by"]]
    assert list(response_transaction) == list(db_transaction)

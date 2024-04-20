from typing import Any

from django.forms.models import model_to_dict
from django.test import Client
from django.urls import reverse

import pytest

from apps.transactions.models import Transaction, Wallet


@pytest.fixture
def updated_transaction_data(
    wallet: Wallet,
    transaction: Transaction,
) -> dict[str, Any]:
    """Generate an updated data for transaction."""
    transaction_data = {
        key: value for key, value in model_to_dict(transaction).items()
        if key not in ["tagged_friends"]
    }

    return {
        **transaction_data,
        "amount": abs(wallet.balance - transaction.amount),
    }


@pytest.fixture
def updated_transaction_data_invalid(
    transaction: Transaction,
) -> dict[str, Any]:
    """Generate an invalid updated data for transaction."""
    transaction_data = {
        key: value for key, value in model_to_dict(transaction).items()
        if key not in ["tagged_friends"]
    }

    return {
        **transaction_data,
        "amount": 0,
    }


def test_transaction_update_view(
    auth_client: Client,
    transaction: Transaction,
    updated_transaction_data: dict[str, Any],
) -> None:
    """Ensure users can modify an existing transaction with valid data."""
    response = auth_client.post(
        reverse("transaction-update", kwargs={"pk": transaction.pk}),
        updated_transaction_data,
    )

    assert response.status_code == 302
    assert Transaction.objects.filter(**updated_transaction_data).exists()


def test_transaction_update_view_invalid(
    auth_client: Client,
    transaction: Transaction,
    updated_transaction_data_invalid: dict[str, Any],
) -> None:
    """Ensure users cannot update an existing transaction with invalid data."""
    response = auth_client.post(
        reverse("transaction-update", kwargs={"pk": transaction.pk}),
        updated_transaction_data_invalid,
    )

    assert response.status_code == 200
    assert not Transaction.objects.filter(
        **updated_transaction_data_invalid,
    ).exists()

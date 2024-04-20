from decimal import Decimal
from typing import Any

from django.forms.models import model_to_dict
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

import pytest
from pytest_lazyfixture import lazy_fixture

from apps.transactions.constants import PREMIUM_USER
from apps.transactions.factories import TransactionFactory
from apps.transactions.models import Transaction, Wallet
from apps.users.factories import UserFactory
from apps.users.models import User


@pytest.fixture
def transaction_data(
    category_pk: int,
    wallet_pk: int,
    wallet_balance: Decimal,
) -> dict[str, Any]:
    """Generate a valid transaction data."""
    return {
        "amount": wallet_balance / 2,
        "category": category_pk,
        "wallet": wallet_pk,
        "date": timezone.now().date(),
        "note": "Test Transaction Note",
        "is_shared": False,
    }


@pytest.fixture
def invalid_data_amount(
    category_pk: int,
    wallet_pk: int,
) -> dict[str, Any]:
    """Generate invalid data that has non positive amount."""
    return {
        "amount": 0,
        "category": category_pk,
        "wallet": wallet_pk,
        "date": timezone.now().date(),
    }


@pytest.fixture
def transactions_premium_by_streak(normal_user: User, wallet: Wallet) -> None:
    """Create a batch of transactions for pre-premium by transaction streak.

    Return a batch of transactions that has PREMIUM_USER["transaction_streak"]
    - 1 transaction streak and qualified transaction count.

    """
    today = timezone.now().date() - timezone.timedelta(days=1)
    num_days = PREMIUM_USER["transaction_streak"] - 1
    num_daily = int(PREMIUM_USER["transaction_count"] / num_days) + 1
    for _ in range(num_days):
        TransactionFactory.create_batch(
            num_daily,
            user=normal_user,
            wallet=wallet,
            date=today,
        )
        today -= timezone.timedelta(days=1)


@pytest.fixture
def transactions_premium_by_count(normal_user: User, wallet: Wallet) -> None:
    """Create a batch of transactions for pre-premium by transaction count.

    Return a batch of transactions that has PREMIUM_USER["transaction_count]
    - 1 transaction count and qualified transaction streak.

    """
    today = timezone.now().date()
    num_days = PREMIUM_USER["transaction_streak"] - 1
    num_transactions = (
        PREMIUM_USER["transaction_count"] - PREMIUM_USER["transaction_streak"]
    )
    for _ in range(num_days):
        TransactionFactory(user=normal_user, date=today, wallet=wallet)
        today -= timezone.timedelta(days=1)
    TransactionFactory.create_batch(
        num_transactions,
        user=normal_user,
        wallet=wallet,
        date=today,
    )


@pytest.fixture
def invalid_data_balance(
    category_pk: int,
    wallet_pk: int,
    wallet_balance: Decimal,
) -> dict[str, Any]:
    """Generate invalid data that has amount greater than wallet's balance."""
    return {
        "amount": wallet_balance * 2,
        "category": category_pk,
        "wallet": wallet_pk,
        "date": timezone.now().date(),
    }


@pytest.fixture
def updated_transaction_data(
    wallet: Wallet,
    transaction: Transaction,
) -> dict[str, Any]:
    """Generate an updated data for transaction."""
    data = {
        key: value for key, value in model_to_dict(transaction).items()
        if key not in ["tagged_friends"]
    }

    return {
        **data,
        "amount": abs(wallet.balance - transaction.amount),
    }


@pytest.fixture
def updated_transaction_data_invalid(
    transaction: Transaction,
) -> dict[str, Any]:
    """Generate an invalid updated data for transaction."""
    data = {
        key: value for key, value in model_to_dict(transaction).items()
        if key not in ["tagged_friends"]
    }

    return {
        **data,
        "amount": 0,
    }


def test_transaction_list_api(api_client: APIClient) -> None:
    """Ensure Transaction list API works properly with status code 200."""
    response = api_client.get(reverse("v1:transaction-list"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data


def test_transaction_list_api_unauthorized() -> None:
    """Raise 401 error for unauthenticated users in Transaction list API."""
    response = APIClient().get(reverse("v1:transaction-list"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_transaction_detail_api(
    api_client: APIClient,
    transaction: Transaction,
) -> None:
    """Ensure Transaction detail API works properly with status code 200."""
    response = api_client.get(
        reverse("v1:transaction-detail", kwargs={"pk": transaction.pk}),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data


def test_transaction_detail_api_unauthorized(transaction: Transaction) -> None:
    """Raise 401 error for unauthenticated users in Transaction detail API."""
    response = APIClient().get(
        reverse("v1:transaction-detail", kwargs={"pk": transaction.pk}),
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_transaction_detail_api_invalid(transaction: Transaction) -> None:
    """Raise 404 when auth users try to access other users' transaction."""
    client = APIClient()
    client.force_authenticate(UserFactory())
    response = client.get(
        reverse("v1:transaction-detail", kwargs={"pk": transaction.pk}),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_transaction_create_api(
    auth_client: Client,
    normal_user: User,
    transaction_data: dict[str, Any],
) -> None:
    """Ensure users can create a new transaction with status code 201."""
    respone = auth_client.post(
        reverse("v1:transaction-list"),
        transaction_data,
    )

    assert respone.status_code == status.HTTP_201_CREATED
    assert Transaction.objects.filter(
        **transaction_data,
        user=normal_user,
    ).exists()


@pytest.mark.parametrize(
    "invalid_transaction_data",
    [
        lazy_fixture("invalid_data_amount"),
        lazy_fixture("invalid_data_balance"),
    ],
)
@pytest.mark.usefixtures("wallet_pk")
def test_transaction_create_api_invalid(
    auth_client: Client,
    normal_user: User,
    invalid_transaction_data: dict[str, Any],
) -> None:
    """Raise 400 error when users create an invalid transaction."""
    respone = auth_client.post(
        reverse("v1:transaction-list"),
        invalid_transaction_data,
    )

    assert respone.status_code == status.HTTP_400_BAD_REQUEST
    assert not Transaction.objects.filter(
        user=normal_user,
        **invalid_transaction_data,
    ).exists()


@pytest.mark.parametrize(
    "pre_premium_transactions",
    [
        lazy_fixture("transactions_premium_by_count"),
        lazy_fixture("transactions_premium_by_streak"),
    ],
)
def test_transaction_create_api_pre_premium(
    auth_client: Client,
    normal_user: User,
    transaction_data: dict[str, Any],
    pre_premium_transactions: Any,  # pylint: disable=unused-argument
) -> None:
    """Ensure users are upgraded to premium after a qualified transaction."""
    response = auth_client.post(
        reverse("v1:transaction-list"),
        transaction_data,
    )
    normal_user.refresh_from_db()

    assert response.status_code == status.HTTP_201_CREATED
    assert normal_user.is_premium


def test_transaction_update_api(
    auth_client: Client,
    transaction: Transaction,
    updated_transaction_data: dict[str, Any],
) -> None:
    """Ensure users can update a transaction with status code 200."""
    response = auth_client.put(
        reverse("v1:transaction-detail", kwargs={"pk": transaction.pk}),
        updated_transaction_data,
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert Transaction.objects.filter(**updated_transaction_data).exists()


def test_transaction_update_api_invalid(
    auth_client: Client,
    transaction: Transaction,
    updated_transaction_data_invalid: dict[str, Any],
) -> None:
    """Raise 400 error when users update a transaction with invalid data."""
    response = auth_client.put(
        reverse("v1:transaction-detail", kwargs={"pk": transaction.pk}),
        updated_transaction_data_invalid,
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not Transaction.objects.filter(
        **updated_transaction_data_invalid,
    ).exists()


def test_transaction_delete_api(
    auth_client: Client,
    transaction: Transaction,
) -> None:
    """Ensure users can delete a transaction with status code 204."""
    response = auth_client.delete(
        reverse("v1:transaction-detail", kwargs={"pk": transaction.pk}),
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Transaction.objects.filter(
        **{
            key: value for key, value in model_to_dict(transaction).items()
            if key not in ["tagged_friends"]
        },
    ).exists()

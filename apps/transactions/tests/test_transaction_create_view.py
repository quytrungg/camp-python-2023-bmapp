from decimal import Decimal
from typing import Any

from django.test import Client
from django.urls import reverse
from django.utils import timezone

import pytest
from pytest_lazyfixture import lazy_fixture

from apps.transactions.constants import PREMIUM_USER
from apps.transactions.factories import TransactionFactory
from apps.transactions.models import Category, Transaction, Wallet
from apps.users.models import User


@pytest.fixture
def transaction_data_view(
    first_default_category: Category,
    wallet: Wallet,
) -> dict[str, Any]:
    """Generate a valid transaction data."""
    return {
        "amount": wallet.balance / 2,
        "category": first_default_category.pk,
        "wallet": wallet.pk,
        "date": timezone.now().date(),
        "note": "Test Transaction Note",
        "is_shared": False,
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
def invalid_data_amount(
    first_default_category: Category,
    wallet: Wallet,
) -> dict[str, Any]:
    """Generate invalid data that has non positive amount."""
    return {
        "amount": 0,
        "category": first_default_category.pk,
        "wallet": wallet.pk,
        "date": timezone.now().date(),
    }


@pytest.fixture
def invalid_data_balance(
    first_default_category: Category,
    wallet: Wallet,
) -> dict[str, Any]:
    """Generate invalid data that has amount greater than wallet's balance."""
    return {
        "amount": wallet.balance * 2,
        "category": first_default_category.pk,
        "wallet": wallet.pk,
        "date": timezone.now().date(),
    }


@pytest.fixture
def invalid_data_shared(
    normal_user: User,
    another_user: User,
    category_pk: int,
    wallet_pk: int,
    wallet_balance: Decimal,
) -> dict[str, Any]:
    """Generate invalid data that tag friends without check the shared box."""
    normal_user.friends.add(another_user)

    return {
        "amount": wallet_balance / 10,
        "category": category_pk,
        "wallet": wallet_pk,
        "date": timezone.now().date(),
        "is_shared": False,
        "tagged_friends": normal_user.friends.all(),
    }


def test_transaction_create_view(
    auth_client: Client,
    normal_user: User,
    transaction_data_view: dict[str, Any],
) -> None:
    """Ensure users can create a new transaction with valid data."""
    response = auth_client.post(
        reverse("transaction-create"),
        transaction_data_view,
    )

    assert response.status_code == 302
    assert Transaction.objects.filter(
        **transaction_data_view,
        user=normal_user,
    ).exists()


@pytest.mark.parametrize(
    "pre_premium_transactions",
    [
        lazy_fixture("transactions_premium_by_count"),
        lazy_fixture("transactions_premium_by_streak"),
    ],
)
def test_transaction_create_view_pre_premium(
    auth_client: Client,
    normal_user: User,
    transaction_data_view: dict[str, Any],
    pre_premium_transactions: Any,  # pylint: disable=unused-argument
) -> None:
    """Ensure users are upgraded to premium after a qualified transaction."""
    response = auth_client.post(
        reverse("transaction-create"),
        transaction_data_view,
    )
    normal_user.refresh_from_db()

    assert response.status_code == 302
    assert normal_user.is_premium


@pytest.mark.parametrize(
    "invalid_transaction_data",
    [
        lazy_fixture("invalid_data_amount"),
        lazy_fixture("invalid_data_balance"),
        lazy_fixture("invalid_data_shared"),
    ],
)
def test_transaction_create_view_invalid(
    auth_client: Client,
    normal_user: User,
    invalid_transaction_data: dict[str, Any],
) -> None:
    """Ensure users cannot make a transaction with invalid data.

    Refuse to create a transaction with amount <= 0 or amount is greater than
    the wallet's balance or any required fields are empty.

    """
    response = auth_client.post(
        reverse("transaction-create"),
        invalid_transaction_data,
    )

    assert response.status_code == 200
    assert not Transaction.objects.filter(
        user=normal_user,
        **{
            key: value for key, value in invalid_transaction_data.items()
            if key not in ["tagged_friends"]
        },
    ).exists()

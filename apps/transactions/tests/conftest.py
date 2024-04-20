from decimal import Decimal
from typing import Any

from django.db.models import Q

import pytest

from apps.rates.models import Currency
from apps.transactions.constants import NORMAL_USER_LIMITS
from apps.transactions.factories import (
    CategoryFactory,
    TransactionFactory,
    WalletFactory,
)
from apps.transactions.models import Category, Transaction, Wallet
from apps.users.models import User


@pytest.fixture(scope="session")
def wallet_create_data(first_currency: Currency) -> dict[str, Any]:
    """Return data for creating a wallet."""
    return {
        "name": "Test Wallet",
        "balance": 100,
        "currency": first_currency.pk,
    }


@pytest.fixture(scope="session")
def category_create_data() -> dict[str, Any]:
    """Provide data for creating a category."""
    return {
        "name": "Test category",
        "is_income": False,
    }


@pytest.fixture
def wallet(normal_user: User) -> Wallet:
    """Generate a wallet."""
    return WalletFactory(user=normal_user)


@pytest.fixture
def wallets(normal_user: User) -> list[Wallet]:
    """Create a few wallets for the user.

    The number of wallets created is one less than the limit.
        (For the purpose of testing create wallet view.)

    The limit is defined in NORMAL_USER_LIMITS["max_wallets_count"] constant.

    """
    return WalletFactory.create_batch(
        NORMAL_USER_LIMITS["max_wallets_count"],
        user=normal_user,
    )


@pytest.fixture
def transaction(normal_user: User, wallet: Wallet) -> Transaction:
    """Generate a transaction."""
    return TransactionFactory(
        user=normal_user,
        wallet=wallet,
        amount=wallet.balance / 10,
    )


@pytest.fixture(scope="session")
def first_default_category() -> Category:
    """Return the first default category."""
    return Category.objects.filter(user__isnull=True).first()


@pytest.fixture
def user_defined_category(django_db_blocker, normal_user: User) -> Category:
    """Return a user-defined category."""
    with django_db_blocker.unblock():
        category = CategoryFactory(user=normal_user)
        yield category
        category.delete()


@pytest.fixture
def category_pk(normal_user: User) -> int:
    """Return the first category object of user in the database."""
    return Category.objects.filter(
        Q(user__isnull=True) | Q(user=normal_user),
    ).first().pk


@pytest.fixture
def wallet_pk(wallet: Wallet) -> int:
    """Return the first wallet's primary key of user in the database."""
    return wallet.pk


@pytest.fixture
def wallet_balance(wallet: Wallet) -> Decimal:
    """Return the first wallet's balance of user in the database."""
    return wallet.balance

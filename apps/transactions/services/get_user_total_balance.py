from decimal import Decimal

from django.db.models import (
    DecimalField,
    ExpressionWrapper,
    F,
    OuterRef,
    Subquery,
    Sum,
)
from django.db.models.functions import Coalesce

from apps.rates.models import Currency, ExchangeRate
from apps.transactions.models import Wallet
from apps.users.models import User

from ..constants import HOME_PAGE_STATS


def get_user_total_balance(
    user: User,
    selected_currency: str,
) -> Decimal:
    """Get user's total balance in all wallets.

    Calculate total balance in all wallets and convert the balance to map
    with the default currency.

    """
    wallets = Wallet.objects.filter(user=user)
    wallets_rate = Subquery(
        ExchangeRate.objects.filter(
            user=user,
            source_currency=OuterRef("currency"),
            destination_currency__code=selected_currency,
        ).values_list("rate")[:1],
    )
    total_balance = wallets.annotate(
        rate_balance=ExpressionWrapper(
            F("balance") * Coalesce(wallets_rate, 1),
            output_field=DecimalField(),
        ),
    ).aggregate(total=Sum("rate_balance"))["total"]

    if not total_balance:
        return Decimal(0)
    return round(total_balance, HOME_PAGE_STATS["max_floating_points"])


def get_user_total_balance_by_currencies(user: User) -> dict[str, Decimal]:
    """Return user's total balance in all types of currencies."""
    user_rates = ExchangeRate.objects.filter(user=user)
    user_currencies = Currency.objects.filter(
        pk__in=user_rates.values_list("source_currency"),
    )
    return {
        currency.code: get_user_total_balance(user, currency.code)
        for currency in user_currencies
    }

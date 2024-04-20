from django.db.models import QuerySet

from apps.rates.models import Currency, ExchangeRate
from apps.users.models import User


def get_user_excluding_currencies(user: User) -> QuerySet:
    """Get list of user's currencies excluding the default currency."""
    user_rates = ExchangeRate.objects.filter(user=user)
    return Currency.objects.filter(
        pk__in=user_rates.values_list("source_currency"),
    ).exclude(code=user.default_currency)

from datetime import date

from django.db.models import QuerySet

from apps.transactions.models import Transaction
from apps.users.models import User


def get_transactions_by_period(
    user: User,
    start: date,
    end: date,
) -> QuerySet:
    """Get list of transactions in a given date range."""
    return Transaction.objects.filter(
        user=user,
        date__gte=start,
        date__lte=end,
    )

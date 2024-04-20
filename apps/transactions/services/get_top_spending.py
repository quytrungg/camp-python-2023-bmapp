from decimal import Decimal

from django.db.models import F, QuerySet, Sum
from django.db.models.functions import Round


def get_top_spending(
    transactions: QuerySet,
    balance_by_period: Decimal,
    amount: int,
) -> QuerySet:
    """Get top spending categories of user in a period of transactions."""
    return transactions.values("category__name").exclude(
        category__is_income=True,
    ).annotate(
        total_category=Sum("amount"),
        percentage=Round(F("total_category") / balance_by_period * 100),
    ).order_by("-total_category")[:amount]

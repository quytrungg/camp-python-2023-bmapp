from decimal import Decimal

from django.db.models import QuerySet, Sum

from ..constants import HOME_PAGE_STATS


def get_total_spending(transactions: QuerySet) -> Decimal:
    """Get total balance in a period of transactions."""
    total = transactions.exclude(category__is_income=True).aggregate(
        total=Sum("amount"),
    )["total"]

    if not total:
        return Decimal(0)
    return round(total, HOME_PAGE_STATS["max_floating_points"])

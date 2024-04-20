from django.db.models import QuerySet

from apps.transactions.models import Transaction
from apps.users.models import User


def get_recent_transactions(user: User, amount: int) -> QuerySet:
    """Get list of user's recent transactions with given amount."""
    return Transaction.objects.filter(user=user).order_by(
        "-date",
    )[:amount].select_related("category")

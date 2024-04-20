from apps.transactions.constants import NORMAL_USER_LIMITS
from apps.transactions.models import Category
from apps.users.models import User


def can_create_more_category(user: User) -> bool:
    """Check if user can create more wallets.

    Normal users can create only
    NORMAL_USER_LIMITS["max_custom_category_count"] wallets.
    Premium users are allowed to create as many as they like.

    """
    if user.is_premium:
        return True

    categories_count = Category.objects.filter(user=user).count()

    return categories_count < NORMAL_USER_LIMITS["max_custom_category_count"]

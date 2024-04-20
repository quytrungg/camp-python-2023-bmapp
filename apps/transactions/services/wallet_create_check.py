from apps.transactions.constants import NORMAL_USER_LIMITS
from apps.transactions.models import Wallet
from apps.users.models import User


def can_create_more_wallets(user: User) -> bool:
    """Check if user can create more wallets.

    Normal users can create only NORMAL_USER_LIMITS["max_wallets_count"]
    wallets.

    Premium users are allowed to create as many as they like.

    """
    if user.is_premium:
        return True

    wallets_count = Wallet.objects.filter(user=user).count()

    return wallets_count < NORMAL_USER_LIMITS["max_wallets_count"]

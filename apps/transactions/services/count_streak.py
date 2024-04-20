import datetime as dt
from functools import reduce

from django.db.models import QuerySet


def count_streak(dates: QuerySet) -> int:
    """Count number of consecutive days users create transaction(s).

    Check in all user's transactions to get the longest transaction streak
    that user have made.

    Example:
        [5, 6, 7, 10, 11] should return 3.
        [1, 3, 5] should return 1.

    """
    if not dates:
        return 0

    streak_count = 1
    current_streak = 1

    def count_consecutive(
        previous: dict,
        current: dict,
    ) -> dt.date:
        """Reduce function to check if 2 dates are consecutive."""
        nonlocal streak_count, current_streak
        if previous["date"] == current["date"] - dt.timedelta(days=1):
            current_streak += 1
        else:
            current_streak = 1
            streak_count = max(streak_count, current_streak)
        return current

    reduce(count_consecutive, dates)
    return max(streak_count, current_streak)

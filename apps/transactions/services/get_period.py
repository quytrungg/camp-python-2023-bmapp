from datetime import date, timedelta


def get_period(now: date, tab: str) -> tuple[date, date]:
    """Provide dates for calculating business logic with given tab.

    Return begin day, previous begin day and previous end day of a given
    period from user choice.

    Args:
        now: today's date object.
        tab: user choice of period (week/month)

    Returns:
        Tuple(date, date, date): begin day, previous begin day and previous
        end day of that period (week/month).

    """
    previous_month = {
        1: 12,
        **{curr: curr - 1 for curr in range(2, 13)},
    }

    if tab == "month":
        begin_period = now.replace(day=1)
        begin_prev_period = begin_period.replace(
            month=previous_month[now.month],
        )
    else:
        begin_period = now - timedelta(days=now.weekday())
        begin_prev_period = begin_period - timedelta(days=7)

    return begin_period, begin_prev_period

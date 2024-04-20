from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView

from ..constants import HOME_PAGE_STATS
from ..services import (
    get_period,
    get_recent_transactions,
    get_top_spending,
    get_total_spending,
    get_transactions_by_period,
    get_user_excluding_currencies,
    get_user_total_balance,
)


class HomeView(LoginRequiredMixin, TemplateView):
    """Provide a homepage view for app."""

    template_name = "home.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Include all business logic for home page view."""
        context = super().get_context_data(**kwargs)
        homepage_data = {}

        homepage_data["currencies"] = get_user_excluding_currencies(
            self.request.user,
        )
        homepage_data["balance"] = get_user_total_balance(
            self.request.user,
            self.request.user.default_currency,
        )
        homepage_data["transactions"] = get_recent_transactions(
            self.request.user,
            HOME_PAGE_STATS["num_recent_transactions"],
        )
        homepage_data["tab"] = self.request.GET.get(
            "tab",
            HOME_PAGE_STATS["default_tab"],
        )

        now = timezone.now()
        begin_period, begin_prev_period = get_period(
            now,
            homepage_data["tab"],
        )
        transactions = get_transactions_by_period(
            self.request.user,
            begin_period,
            now,
        )
        total_period = get_total_spending(transactions)
        prev_transactions = get_transactions_by_period(
            self.request.user,
            begin_prev_period,
            begin_period - timezone.timedelta(days=1),
        )
        total_prev_period = get_total_spending(prev_transactions)

        homepage_data["total_period"] = total_period
        homepage_data["total_prev_period"] = total_prev_period
        homepage_data["top_spending"] = get_top_spending(
            transactions,
            total_period,
            HOME_PAGE_STATS["num_top_spending"],
        )

        if total_prev_period == 0:
            homepage_data["stats"] = 100
        else:
            stats = (total_period - total_prev_period) / total_prev_period
            stats_percent = stats * 100
            homepage_data["stats"] = round(stats_percent)

        context.update(homepage_data)
        return context

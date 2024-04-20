from django.utils import timezone

from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from apps.transactions.constants import HOME_PAGE_STATS
from apps.transactions.services import (
    get_period,
    get_recent_transactions,
    get_top_spending,
    get_total_spending,
    get_transactions_by_period,
    get_user_excluding_currencies,
    get_user_total_balance_by_currencies,
)

from .serializers import HomeSerializer


class HomeView(GenericAPIView):
    """Provide API view for home page.

    The business-required information for home page includes:
        - Total balance
        - Default currency
        - Top spending in month/week
        - Total spending in month/week
        - Percentage compared to last month/week
        - Recent transactions

    """

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = HomeSerializer

    def get(self, request: Request, *args, **kwargs) -> Response:
        """Retrieve business-required information for home page view."""
        homepage_data = {}
        homepage_data["excluding_currencies"] = get_user_excluding_currencies(
            request.user,
        )
        homepage_data["total_balance"] = get_user_total_balance_by_currencies(
            request.user,
        )
        homepage_data["recent_transactions"] = get_recent_transactions(
            request.user,
            HOME_PAGE_STATS["num_recent_transactions"],
        )
        homepage_data["tab"] = request.GET.get(
            "tab",
            HOME_PAGE_STATS["default_tab"],
        )

        now = timezone.now()
        begin_period, begin_prev_period = get_period(
            now,
            homepage_data["tab"],
        )
        transactions = get_transactions_by_period(
            request.user,
            begin_period,
            now,
        )
        total_period = get_total_spending(transactions)
        prev_transactions = get_transactions_by_period(
            request.user,
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

        return Response(
            HomeSerializer(homepage_data).data,
            status=status.HTTP_200_OK,
        )

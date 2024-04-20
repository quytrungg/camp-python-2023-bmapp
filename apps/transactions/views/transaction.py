from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from apps.core.views import BaseListView

from ..constants import PREMIUM_USER
from ..filters import TransactionFilter
from ..forms import TransactionForm
from ..models import Transaction
from ..services import count_streak


class TransactionListView(LoginRequiredMixin, BaseListView):
    """Provide list page for Transaction model.

    Users can view list of their transactions from Transaction tab in homepage.

    """

    model = Transaction
    context_object_name = "transactions"
    template_name = "transactions/transactions/transaction_list.html"
    filter_class = TransactionFilter

    def get_queryset(self) -> QuerySet:
        """Get queryset from base class and filter all user's transactions."""
        qs = super().get_queryset()
        return qs.filter(user=self.request.user).order_by("-date")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add default category to context data for rendering template UI."""
        context = super().get_context_data(**kwargs)
        context["default_currency"] = self.request.user.default_currency
        return context


class TransactionCreateView(LoginRequiredMixin, CreateView):
    """Provide create page for Transaction model.

    Users can create a new transaction, after creation, users with qualified
    transaction count and transaction streak will be upgraded to premium user.
    Qualified criterias are listed in `PREMIUM_USER` constant.

    """

    model = Transaction
    template_name = "transactions/transactions/transaction_form.html"
    success_url = reverse_lazy("home")
    form_class = TransactionForm

    def form_valid(self, form: TransactionForm) -> HttpResponse:
        """Check if user is qualified for premium mode.

        Users must surpass transaction count and transaction streak threshold
        to be upgraded as premium account. All criterias are listed in
        `PREMIUM_USER` constant.

        """
        if self.request.user.is_premium:
            return super().form_valid(form)

        today = timezone.now()
        transaction_dates = Transaction.objects.filter(
            user=self.request.user,
            date__lte=today,
        ).order_by("date").values("date")
        transaction_count = transaction_dates.count()
        transaction_streak = count_streak(transaction_dates.distinct())

        if (
            transaction_count >= PREMIUM_USER["transaction_count"] - 1 and
            transaction_streak >= PREMIUM_USER["transaction_streak"] - 1
        ):
            self.request.user.is_premium = True
            self.request.user.save()
            messages.add_message(
                self.request,
                messages.INFO,
                f"You have made over {PREMIUM_USER['transaction_count']} "
                f"transactions and {PREMIUM_USER['transaction_streak']} day "
                "transaction streak. Your account is now upgraded to premium.",
            )

        return super().form_valid(form)

    def get_form_kwargs(self) -> dict[str, Any]:
        """Add the request user to the form's kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class TransactionDetailView(LoginRequiredMixin, DetailView):
    """Provide detail page for Transaction model."""

    model = Transaction
    context_object_name = "transaction"
    template_name = "transactions/transactions/transaction_detail.html"

    def get_queryset(self) -> QuerySet[Any]:
        """Add transaction's category to the queryset."""
        return super().get_queryset().select_related("category").filter(
            user=self.request.user,
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add transaction detail to context.

        Raise 404 error if the transaction detail does not exist or if the
        transaction does not belong to the current user. Get related
        information for template UI.

        """
        context = super().get_context_data(**kwargs)
        transaction_data = {}

        transaction_data["income"] = context["transaction"].category.is_income
        transaction_data["currency"] = self.request.user.default_currency

        context.update(transaction_data)
        return context


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    """Provide update view page for Transaction model."""

    model = Transaction
    template_name = "transactions/transactions/transaction_form.html"
    success_url = reverse_lazy("transaction-list")
    form_class = TransactionForm

    def get_queryset(self) -> QuerySet[Any]:
        """Restrict users from accessing other users' transactions."""
        return super().get_queryset().filter(user=self.request.user)

    def get_form_kwargs(self) -> dict[str, Any]:
        """Add the request user to the form's kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    """Provide delete view for Transaction model."""

    model = Transaction
    context_object_name = "transaction"
    template_name = "transactions/transactions/transaction_delete.html"
    success_url = reverse_lazy("transaction-list")

from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView

from apps.core.views import BaseListView
from apps.transactions.filters import TransactionFilter, WalletFilter
from apps.transactions.forms import WalletForm, WalletUpdateForm
from apps.transactions.models import Transaction, Wallet


class WalletListView(LoginRequiredMixin, BaseListView):
    """Provide a view for listing all wallets of a user."""

    model = Wallet
    template_name = "transactions/wallets/wallet_list.html"
    context_object_name = "wallets"
    filter_class = WalletFilter

    def get_queryset(self):
        """Return a queryset of wallets for the current user."""
        qs = super().get_queryset()
        return qs.select_related(
            "bank", "currency",
        ).filter(
            user=self.request.user,
        ).order_by("name")


class WalletCreateView(LoginRequiredMixin, CreateView):
    """Provide a view for creating a new wallet."""

    model = Wallet
    template_name = "transactions/wallets/wallet_create_update.html"
    form_class = WalletForm
    success_url = reverse_lazy("wallet-list")

    def get_form_kwargs(self) -> dict[str, Any]:
        """Add the 'user' keyword argument to the form's kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class WalletDetailView(LoginRequiredMixin, BaseListView):
    """Provide a view for detail of a wallet.

    Details are: name, bank, currency, balance, transactions with that wallet.

    This view actually focus on the list of transactions within this wallet,
        therefore we can consider it as a BaseListView for Transaction model.
    By setting model = Transaction and changing logic in get_queryset() and
        get_context_data(), we can remove the similar/duplicated queries
        to database.

    """

    model = Transaction
    template_name = "transactions/wallets/wallet_detail.html"
    context_object_name = "transactions"
    filter_class = TransactionFilter

    def get_queryset(self) -> QuerySet:
        """Return a queryset of transactions for the this user and wallet."""
        return super().get_queryset().filter(
            user=self.request.user,
            wallet=self.kwargs["pk"],
        ).order_by("-date")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add the wallet to the context data.

        Raise Http404 if the wallet does not exist
        or if the wallet does not belong to the current user.

        """
        context_data = super().get_context_data(**kwargs)
        wallet = get_object_or_404(
            Wallet,
            pk=self.kwargs["pk"],
            user=self.request.user,
        )
        context_data["wallet"] = wallet
        return context_data


class WalletUpdateView(LoginRequiredMixin, UpdateView):
    """Provide a view for updating a wallet."""

    model = Wallet
    template_name = "transactions/wallets/wallet_create_update.html"
    form_class = WalletUpdateForm
    success_url = reverse_lazy("wallet-list")
    context_object_name = "wallet"

    def get_queryset(self) -> QuerySet:
        """Return a queryset of wallets for the this user."""
        return super().get_queryset().filter(
            user=self.request.user,
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["updated"] = True
        return context

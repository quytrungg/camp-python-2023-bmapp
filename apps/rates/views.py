from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView

from apps.core.views import BaseListView
from apps.rates.filters import ExchangeRateFilter
from apps.rates.forms import ExchangeRateCreateForm, ExchangeRateUpdateForm
from apps.rates.models import ExchangeRate


class ExchangeRateListView(LoginRequiredMixin, BaseListView):
    """Provide a view for listing all exchange rates of a user."""

    model = ExchangeRate
    template_name = "rates/rate_list.html"
    context_object_name = "rates"
    filter_class = ExchangeRateFilter

    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()
        return qs.filter(user=self.request.user).order_by("source_currency")


class ExchangeRateCreateView(LoginRequiredMixin, CreateView):
    """Provide a view for creating a new exchange rate."""

    model = ExchangeRate
    template_name = "rates/rate_form.html"
    form_class = ExchangeRateCreateForm
    success_url = reverse_lazy("rate-list")
    context_object_name = "rate"

    def get_form_kwargs(self) -> dict[str, Any]:
        """Add the 'user' keyword argument to the form's kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class ExchangeRateUpdateView(LoginRequiredMixin, UpdateView):
    """Provide a view for updating an exchange rate."""

    model = ExchangeRate
    template_name = "rates/rate_form.html"
    form_class = ExchangeRateUpdateForm
    success_url = reverse_lazy("rate-list")
    context_object_name = "rate"

    def get_form_kwargs(self) -> dict[str, Any]:
        """Add the 'user' keyword argument to the form's kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(user=self.request.user)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add the 'updated' variable to the context.

        To notice for the form that this is an update view.

        """
        context = super().get_context_data(**kwargs)
        context["updated"] = True
        return context

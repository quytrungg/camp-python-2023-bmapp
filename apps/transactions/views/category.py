from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView

from apps.core.views import BaseListView
from apps.transactions.filters import CategoryFilter, TransactionFilter
from apps.transactions.forms import CategoryForm, CategoryUpdateForm
from apps.transactions.models import Category, Transaction


class CategoryListView(LoginRequiredMixin, BaseListView):
    """Provide list page for Category model.

    Users can view list of default categories and their custom categories.

    """

    model = Category
    context_object_name = "categories"
    template_name = "transactions/categories/category_list.html"
    filter_class = CategoryFilter

    def get_queryset(self) -> QuerySet:
        """Get queryset from base class and add custom filter."""
        qs = super().get_queryset()
        return qs.filter(
            Q(user__isnull=True) | Q(user=self.request.user),
        ).order_by("name")


class CategoryCreateView(LoginRequiredMixin, CreateView):
    """Provide create page for Category model.

    Users can create a new custom category, providing category's name and
    indicate whether it is an income or expense category.

    """

    model = Category
    template_name = "transactions/categories/category_form.html"
    success_url = reverse_lazy("category-list")
    form_class = CategoryForm

    def get_form_kwargs(self) -> dict[str, Any]:
        """Add the request user to the form's kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class CategoryDetailView(LoginRequiredMixin, BaseListView):
    """Provide a view for details of a category."""

    model = Transaction
    template_name = "transactions/categories/category_detail.html"
    context_object_name = "transactions"
    filter_class = TransactionFilter

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add the category to the context data.

        Raise Http404 if the category does not exist
        or if the category does not belong to the current user.

        This view actually focus on the list of transactions within
            this category, therefore we can consider it as a BaseListView
            for Transaction model.
        By setting model = Transaction and changing logic in get_queryset() and
            get_context_data(), we can remove the similar/duplicated queries
            to database.

        """
        context_data = super().get_context_data(**kwargs)
        category = get_object_or_404(
            Category,
            Q(user=self.request.user) | Q(user__isnull=True),
            pk=self.kwargs["pk"],
        )
        context_data["category"] = category

        return context_data

    def get_queryset(self) -> QuerySet[Any]:
        """Return a queryset of transactions for this user and category."""
        return super().get_queryset().filter(
            user=self.request.user,
            category=self.kwargs["pk"],
        ).order_by("-date")


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    """Provide a view for updating a category."""

    model = Category
    template_name = "transactions/categories/category_form.html"
    success_url = reverse_lazy("category-list")
    form_class = CategoryUpdateForm
    context_object_name = "category"

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(
            user=self.request.user,
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["updated"] = True
        return context

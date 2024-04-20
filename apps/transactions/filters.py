from django.db.models import Q

import django_filters

from apps.transactions.models import Category, Transaction, Wallet


class CategoryFilter(django_filters.FilterSet):
    """Provide filtering options for Category model."""

    name = django_filters.CharFilter(lookup_expr="icontains")
    is_income = django_filters.BooleanFilter()

    class Meta:
        model = Category
        fields = ["name", "is_income"]


class WalletFilter(django_filters.FilterSet):
    """Provide filtering options for Wallet model."""

    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Wallet
        fields = ["name", "bank", "currency"]


class TransactionFilter(django_filters.FilterSet):
    """Provide filtering options for Transaction model."""

    amount = django_filters.RangeFilter(field_name="amount")
    category = django_filters.ModelChoiceFilter(
        queryset=lambda request: Category.objects.filter(
            Q(user__isnull=True) | Q(user=request.user),
        ),
    )
    wallet = django_filters.ModelChoiceFilter(
        queryset=lambda request: Wallet.objects.filter(user=request.user),
    )
    date = django_filters.DateRangeFilter()
    note = django_filters.CharFilter(lookup_expr="icontains")
    is_shared = django_filters.BooleanFilter()

    class Meta:
        model = Transaction
        fields = ["amount", "category", "wallet", "date", "note", "is_shared"]

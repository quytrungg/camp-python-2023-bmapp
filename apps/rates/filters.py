import django_filters

from apps.rates.models import ExchangeRate


class ExchangeRateFilter(django_filters.FilterSet):
    """Provide filtering options for ExchangeRate model."""

    class Meta:
        model = ExchangeRate
        fields = ["source_currency", "destination_currency"]

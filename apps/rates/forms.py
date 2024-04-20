from decimal import Decimal
from typing import Any

from django.forms import DecimalField, ModelForm, ValidationError

from apps.rates.models import ExchangeRate


class ExchangeRateCreateForm(ModelForm):
    """Provide a form for ExchangeRate model at create page."""

    user = None
    rate = DecimalField(
        decimal_places=6,
        max_digits=14,
        min_value=0.000001,  # Rate must not be zero
    )

    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, Any]:
        """Check if there exists a duplication of exchange rate."""
        source_currency = self.cleaned_data.get("source_currency")
        destination_currency = self.cleaned_data.get("destination_currency")

        if source_currency == destination_currency:
            raise ValidationError(
                "The source currency and the destination currency must differ",
            )

        if ExchangeRate.objects.filter(
            user=self.user,
            source_currency=source_currency,
            destination_currency=destination_currency,
        ).exists():
            raise ValidationError(
                "This exchange rate already exists.",
            )

        return super().clean()

    def save(self, *args, **kwargs):
        """Save the form with instance user is the request user.

        Moreover, after saving a form which specify the exchange rate
            between source_currency and destination_currency,
            we also create the reverse exchange rate between
            destination_currency and source_currency.

        """
        self.instance.user = self.user
        instance = super().save(*args, **kwargs)

        reverse_rate = ExchangeRate(
            user=self.user,
            source_currency=self.instance.destination_currency,
            destination_currency=self.instance.source_currency,
            rate=Decimal(1) / self.instance.rate,
        )
        reverse_rate.save()

        return instance

    class Meta:
        model = ExchangeRate
        fields = ("source_currency", "destination_currency", "rate")


class ExchangeRateUpdateForm(ModelForm):
    """Provide a form for updating an exchange rate."""

    user = None
    rate = DecimalField(
        decimal_places=6,
        max_digits=14,
        min_value=0.000001,  # Rate must not be zero
    )

    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        """Update the reverse rate if this is an UpdateView."""
        reverse_rate = ExchangeRate.objects.get(
            user=self.user,
            source_currency=self.instance.destination_currency,
            destination_currency=self.instance.source_currency,
        )
        reverse_rate.rate = Decimal(1) / self.instance.rate
        reverse_rate.save()

        return super().save(*args, **kwargs)

    class Meta:
        model = ExchangeRate
        fields = ("rate",)

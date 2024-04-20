from rest_framework import serializers

from apps.core.api.serializers import ModelBaseSerializer
from apps.core.exceptions import ValidationError
from apps.rates.models import Currency, ExchangeRate


class CurrencySerializer(ModelBaseSerializer):
    """Serializer for Currency model."""

    class Meta:
        model = Currency
        fields = ("code",)
        read_only_fields = ("id", "name", "code")


class ExchangeRateSerializer(ModelBaseSerializer):
    """Serializer for ExchangeRate model."""

    source_currency = serializers.CharField(source="source_currency.code")
    destination_currency = serializers.CharField(
        source="destination_currency.code",
    )

    def validate(self, attrs: dict) -> dict:
        """Validate that source and destination currency are different."""
        if (
            attrs["source_currency"]["code"] ==
            attrs["destination_currency"]["code"]
        ):
            raise ValidationError(
                "Source and destination currencies must be different.",
            )
        return super().validate(attrs)

    def create(self, validated_data):
        """Create new exchange rate.

        Check if source and destination currency is the same,
        also check if exchange rate already exists.

        Automatically create the reverse exchange rate.

        """
        validated_src_currency = validated_data["source_currency"]["code"]
        validated_dest_currency = (
            validated_data["destination_currency"]["code"]
        )

        # Check if exchange rate already exists.
        if ExchangeRate.objects.filter(
            source_currency__code=validated_src_currency,
            destination_currency__code=validated_dest_currency,
            user=self.context["request"].user,
        ).exists():
            raise ValidationError(
                "Exchange rate already exists.",
            )

        src_currency = Currency.objects.get(
            code=validated_src_currency,
        )
        dest_currency = Currency.objects.get(
            code=validated_dest_currency,
        )

        validated_data["source_currency"] = src_currency
        validated_data["destination_currency"] = dest_currency

        validated_data["user"] = self.context["request"].user

        # Create the reverse exchange rate.
        ExchangeRate.objects.create(
            source_currency=dest_currency,
            destination_currency=src_currency,
            rate=1 / validated_data["rate"],
            user=self.context["request"].user,
        )

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Do not allow user to update source and destination currency.

        Automatically update the reverse exchange rate.

        """
        validated_data.pop("source_currency", None)
        validated_data.pop("destination_currency", None)

        # Update the reverse exchange rate.
        ExchangeRate.objects.filter(
            source_currency=instance.destination_currency,
            destination_currency=instance.source_currency,
        ).update(
            rate=1 / validated_data["rate"],
        )

        return super().update(instance, validated_data)

    class Meta:
        model = ExchangeRate
        fields = (
            "id",
            "source_currency",
            "destination_currency",
            "rate",
        )
        read_only_fields = ("id", "source_currency", "destination_currency")

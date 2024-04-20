from typing import Any

from apps.core.api.serializers import ModelBaseSerializer
from apps.core.exceptions import NonFieldValidationError
from apps.rates.models import ExchangeRate
from apps.transactions.api.transactions.serializers import (
    TransactionSerializer,
)
from apps.transactions.models import Wallet
from apps.transactions.services import can_create_more_wallets


class WalletSerializer(ModelBaseSerializer):
    """Serializer for representing `Wallet`."""

    transactions = TransactionSerializer(
        source="transaction_set",
        many=True,
        read_only=True,
    )

    def validate(self, attrs: dict) -> dict:
        """Validate that there is an exchange rate for the currency."""
        if (
            "currency" in attrs and
            attrs["currency"].code != (
                self.context["request"].user.default_currency
            )
        ):
            if not ExchangeRate.objects.filter(
                source_currency=attrs["currency"],
                destination_currency__code=(
                    self.context["request"].user.default_currency
                ),
            ).exists():
                raise NonFieldValidationError(
                    "There is no exchange rate for this currency.",
                )

        return super().validate(attrs)

    def create(self, validated_data) -> Any:
        """Create new wallet for authenticated user.

        Raise NonFieldValidationError if user can't create more wallets, e.g.
        they are not premium and they have already reached the limit of
        wallets.

        Add authenticated user to the validated data.

        """
        if not can_create_more_wallets(self.context["request"].user):
            raise NonFieldValidationError(
                "You can't create more wallets. Please upgrade to premium.",
            )

        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data) -> Any:
        """Update the data of the wallet.

        Do not allow user to change the wallet's user, currency,
        and transactions.

        Raise NonFieldValidationError if user tries to change the currency of
        the wallet.

        """
        validated_data.pop("currency", None)

        return super().update(instance, validated_data)

    class Meta:
        model = Wallet
        fields = (
            "id",
            "name",
            "user",
            "bank",
            "balance",
            "currency",
            "transactions",
        )
        read_only_fields = (
            "user",
            "transactions",
        )

from decimal import Decimal

from django.utils import timezone

from rest_framework.exceptions import ValidationError

from apps.core.api.serializers import ModelBaseSerializer
from apps.rates.models import ExchangeRate
from apps.transactions.constants import PREMIUM_USER
from apps.transactions.models import Transaction
from apps.transactions.services import count_streak
from apps.users.api.serializers import UserSerializer


class TransactionSerializer(ModelBaseSerializer):
    """Provide Serializer class for Transaction model."""

    user = UserSerializer(read_only=True)

    def validate(self, attrs: dict) -> dict:
        """Validate transaction data before create or update.

        Restrict user from entering an amount that is greater than the wallet's
        balance. Hence, check if current user is qualified to become premium
        user.

        """
        attrs = super().validate(attrs)

        amount = attrs["amount"]
        category = attrs["category"]
        wallet = attrs["wallet"]
        rate_obj = ExchangeRate.objects.filter(
            user=self._request.user,
            source_currency=wallet.currency,
            destination_currency__code=self._request.user.default_currency,
        ).first()

        rate = rate_obj.rate if rate_obj else Decimal(1)

        if not category.is_income and amount > wallet.balance * rate:
            raise ValidationError(
                "Amount cannot be greater than wallet's balance",
            )

        if self._request.user.is_premium:
            return attrs

        today = timezone.now()
        transaction_dates = Transaction.objects.filter(
            user=self._request.user,
            date__lte=today,
        ).order_by("date").values("date")
        transaction_count = transaction_dates.count()
        transaction_streak = count_streak(transaction_dates.distinct())

        if (
            transaction_count >= PREMIUM_USER["transaction_count"] - 1 and
            transaction_streak >= PREMIUM_USER["transaction_streak"] - 1
        ):
            self._request.user.is_premium = True
            self._request.user.save()

        return attrs

    class Meta:
        model = Transaction
        fields = (
            "amount",
            "user",
            "category",
            "wallet",
            "date",
            "note",
            "is_shared",
        )
        read_only_fields = ("id", "user")

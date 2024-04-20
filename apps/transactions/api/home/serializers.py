from rest_framework import serializers

from apps.rates.api.serializers import CurrencySerializer
from apps.transactions.api.transactions.serializers import (
    TransactionSerializer,
)


class TopSpendingSerializer(serializers.Serializer):
    """Provide Serializer class for top spending data."""

    category__name = serializers.CharField()
    total_category = serializers.DecimalField(max_digits=20, decimal_places=3)
    percentage = serializers.DecimalField(max_digits=20, decimal_places=3)

    class Meta:
        fields = "__all__"

    def create(self, validated_data):
        """Escape warning."""

    def update(self, instance, validated_data):
        """Escape warning."""


class HomeSerializer(serializers.Serializer):
    """Provide Serializer class for home page API."""

    excluding_currencies = CurrencySerializer(many=True)
    total_balance = serializers.DictField()
    recent_transactions = TransactionSerializer(many=True)
    tab = serializers.CharField()
    total_period = serializers.DecimalField(max_digits=20, decimal_places=3)
    top_spending = TopSpendingSerializer(many=True)
    stats = serializers.DecimalField(max_digits=20, decimal_places=3)
    total_prev_period = serializers.DecimalField(
        max_digits=20,
        decimal_places=3,
    )

    class Meta:
        fields = "__all__"

    def create(self, validated_data):
        """Escape warning."""

    def update(self, instance, validated_data):
        """Escape warning."""

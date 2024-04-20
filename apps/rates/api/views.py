from rest_framework import mixins

from apps.core.api.mixins import UpdateModelWithoutPatchMixin
from apps.core.api.views import BaseViewSet
from apps.rates.models import ExchangeRate

from .serializers import ExchangeRateSerializer


class ExchangeRateViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    UpdateModelWithoutPatchMixin,
    BaseViewSet,
):
    """List all available exchange rates for authenticated user."""

    serializer_class = ExchangeRateSerializer
    ordering_fields = ("source_currency", "destination_currency")
    search_fields = ("source_currency", "destination_currency")
    queryset = ExchangeRate.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(
            user=self.request.user,
        ).order_by("source_currency")

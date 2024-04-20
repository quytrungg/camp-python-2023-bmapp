from rest_framework import mixins

from apps.core.api.mixins import UpdateModelWithoutPatchMixin
from apps.core.api.views import BaseViewSet
from apps.transactions.models import Wallet

from .serializers import WalletSerializer


class WalletViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    UpdateModelWithoutPatchMixin,
    BaseViewSet,
):
    """View set for Wallet model."""

    serializer_class = WalletSerializer
    ordering_fields = ("name", "balance")
    search_fields = ("name",)
    queryset = Wallet.objects.all()

    def get_queryset(self):
        """Return all wallets for authenticated user."""
        return Wallet.objects.filter(user=self.request.user)

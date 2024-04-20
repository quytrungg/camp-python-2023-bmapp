from django.db.models import Prefetch, Q

from rest_framework import mixins

from apps.core.api.mixins import UpdateModelWithoutPatchMixin
from apps.core.api.views import BaseViewSet
from apps.transactions.models import Category

from .serializers import CategoryDetailSerializer, CategoryListSerializer


class CategoryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    UpdateModelWithoutPatchMixin,
    BaseViewSet,
):
    """View set for Category model."""

    serializer_class = CategoryListSerializer
    ordering_fields = ("name", "balance")
    search_fields = ("name",)
    queryset = Category.objects.all()
    serializers_map = {
        "list": CategoryListSerializer,
        "retrieve": CategoryDetailSerializer,
        "default": CategoryListSerializer,
    }

    def get_queryset(self):
        """Return all categories for the authenticated user."""
        qs = super().get_queryset().filter(
            Q(user=self.request.user) | Q(user__isnull=True),
        )
        if self.action == "list":
            return qs
        return qs.prefetch_related(
            Prefetch(
                "transaction_set",
                queryset=self.request.user.transaction_set.all(),
                to_attr="transactions",
            ),
        )

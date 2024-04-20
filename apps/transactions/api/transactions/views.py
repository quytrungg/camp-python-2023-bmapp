from django.db.models import QuerySet

from rest_framework import mixins, status
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.api.mixins import UpdateModelWithoutPatchMixin
from apps.core.api.views import BaseViewSet
from apps.transactions.models import Transaction

from .serializers import TransactionSerializer


class TransactionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    UpdateModelWithoutPatchMixin,
    mixins.DestroyModelMixin,
    BaseViewSet,
):
    """Provide API ViewSet for Transaction model."""

    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
    ordering_fields = ("amount", "date")
    search_fields = (
        "amount",
        "date",
        "category",
        "wallet",
        "note",
        "is_shared",
    )

    def get_queryset(self) -> QuerySet:
        """Return transactions only from current authenticated user."""
        return Transaction.objects.filter(
            user=self.request.user,
        ).order_by("-date")

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Set the user to the current authenticated user."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.validated_data["user"] = request.user
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

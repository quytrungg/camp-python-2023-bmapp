from django.urls import path

from ..views import (
    TransactionCreateView,
    TransactionDeleteView,
    TransactionDetailView,
    TransactionListView,
    TransactionUpdateView,
)

urlpatterns = [
    path("", TransactionListView.as_view(), name="transaction-list"),
    path(
        "create/",
        TransactionCreateView.as_view(),
        name="transaction-create",
    ),
    path(
        "<int:pk>/",
        TransactionDetailView.as_view(),
        name="transaction-detail",
    ),
    path(
        "update/<int:pk>/",
        TransactionUpdateView.as_view(),
        name="transaction-update",
    ),
    path(
        "delete/<int:pk>/",
        TransactionDeleteView.as_view(),
        name="transaction-delete",
    ),
]

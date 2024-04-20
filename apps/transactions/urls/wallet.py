from django.urls import path

from apps.transactions.views import (
    WalletCreateView,
    WalletDetailView,
    WalletListView,
    WalletUpdateView,
)

urlpatterns = [
    path("", WalletListView.as_view(), name="wallet-list"),
    path("create/", WalletCreateView.as_view(), name="wallet-create"),
    path("<int:pk>/", WalletDetailView.as_view(), name="wallet-detail"),
    path("update/<int:pk>/", WalletUpdateView.as_view(), name="wallet-update"),
]

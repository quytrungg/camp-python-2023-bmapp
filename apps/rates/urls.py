from django.urls import path

from apps.rates.views import (
    ExchangeRateCreateView,
    ExchangeRateListView,
    ExchangeRateUpdateView,
)

urlpatterns = [
    path("", ExchangeRateListView.as_view(), name="rate-list"),
    path("create/", ExchangeRateCreateView.as_view(), name="rate-create"),
    path(
        "update/<int:pk>/",
        ExchangeRateUpdateView.as_view(),
        name="rate-update",
    ),
]

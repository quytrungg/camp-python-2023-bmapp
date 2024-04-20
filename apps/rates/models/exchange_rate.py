from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel
from apps.users.models import User


class ExchangeRate(BaseModel):
    """Custom exchange rate of users.

    Attrs:
        user: referenced to User, identified the user who owns this rate
        source_currency * rate = destination_currency

    """

    user = models.ForeignKey(
        verbose_name=_("User of this rate"),
        to=User,
        on_delete=models.CASCADE,
    )

    source_currency = models.ForeignKey(
        verbose_name=_("Source currency"),
        to="rates.Currency",
        on_delete=models.CASCADE,
        related_name="source_rates",
    )

    destination_currency = models.ForeignKey(
        verbose_name=_("Destination currency"),
        to="rates.Currency",
        on_delete=models.CASCADE,
        related_name="destination_rates",
    )

    rate = models.DecimalField(
        verbose_name=_("Exchange rate"),
        decimal_places=6,
        max_digits=14,
    )

    class Meta:
        verbose_name = _("Exchange rate")
        verbose_name_plural = _("Exchange rates")

    def __str__(self):
        return (
            f"{self.source_currency.code} to "
            f"{self.destination_currency.code}"
        )

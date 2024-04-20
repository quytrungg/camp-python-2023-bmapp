from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel
from apps.users.models import User


class Wallet(BaseModel):
    """Create model for Wallet.

    Attrs:
        name: name of the wallet
        user: user's id, indicate the wallet's owner
        bank: bank's id, indicate whether this wallet is bank linked
        balance: amount of money in this wallet

    """

    name = models.CharField(
        verbose_name=_("Wallet"),
        max_length=20,
    )
    user = models.ForeignKey(
        to=User,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
    )
    bank = models.ForeignKey(
        to="transactions.Bank",
        verbose_name=_("Bank"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    balance = models.DecimalField(
        verbose_name=_("Balance"),
        default=0,
        max_digits=20,
        decimal_places=3,
    )
    currency = models.ForeignKey(
        to="rates.Currency",
        verbose_name=_("Currency"),
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        verbose_name = _("Wallet")
        verbose_name_plural = _("Wallets")

    def __str__(self) -> str:
        return self.name

    def set_balance(self, new_balance: Decimal) -> None:
        """Set balance for Wallet model and save."""
        self.balance = new_balance
        self.save()

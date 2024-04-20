from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel
from apps.users.models import User


def validate_positive(value) -> None:
    """Ensure amount has positive value."""
    if value <= 0:
        raise ValidationError(
            _("%(value)s must have positive value."),
            params={"value": value},
        )


class Transaction(BaseModel):
    """Create model for Transaction.

    Attrs:
        user: user's id, the person who makes this transaction
        amount: amount of money in this transaction
        category: category's, indicate the category of this transaction
        wallet: wallet's id, indicate which wallet will be used
        date: the date user choose to make this transaction
        note: additional information/note of this transaction
        is_shared: indicate whether this is a shared bill transactions

    """

    user = models.ForeignKey(
        to=User,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
    )
    amount = models.DecimalField(
        verbose_name=_("Amount"),
        default=0,
        max_digits=20,
        decimal_places=3,
        validators=[validate_positive],
    )
    category = models.ForeignKey(
        to="transactions.Category",
        verbose_name=_("Category"),
        on_delete=models.CASCADE,
    )
    wallet = models.ForeignKey(
        to="transactions.Wallet",
        verbose_name=_("Wallet"),
        on_delete=models.CASCADE,
    )
    date = models.DateField(
        verbose_name=_("Date"),
        default=timezone.localdate,
    )
    note = models.TextField(
        verbose_name=_("Note"),
        null=False,
        blank=True,
    )
    is_shared = models.BooleanField(
        verbose_name=_("Shared"),
        default=False,
    )
    tagged_friends = models.ManyToManyField(
        verbose_name=_("Friends"),
        to=User,
        through="SharedBill",
        related_name="tagged_friends",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")

    def __str__(self) -> str:
        return f"{self.user}: {self.category} - {self.amount} ({self.date})"

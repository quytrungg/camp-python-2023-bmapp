from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel
from apps.users.models import User


class SharedBill(BaseModel):
    """Create model for SharedBill, a special type of Transaction.

    Attrs:
        transaction: transaction's id of this shared bill
        friend: friend's id that is involved in the shared bill transaction

    """

    transaction = models.ForeignKey(
        to="transactions.Transaction",
        verbose_name=_("Transaction ID"),
        on_delete=models.CASCADE,
    )
    friend = models.ForeignKey(
        to=User,
        verbose_name=_("Friend"),
        on_delete=models.CASCADE,
    )

from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel
from apps.rates import constants


class Currency(BaseModel):
    """Currency names and codes for rates.

    Attrs:
        name: Name of the currency.
        code: Code of the currency (3 uppercase letters)

    """

    name = models.CharField(
        verbose_name=_("Currency name"),
        max_length=50,
        default=constants.DEFAULT_CURRENCY_NAME,
    )

    code = models.CharField(
        verbose_name=_("Currency code"),
        max_length=3,
        unique=True,
        default=constants.DEFAULT_CURRENCY_CODE,
        validators=[
            RegexValidator(r"^[A-Z]{3}$", "Code must be 3 uppercase letters."),
        ],
    )

    class Meta:
        verbose_name = _("Currency")
        verbose_name_plural = _("Currencies")

    def __str__(self):
        return self.code

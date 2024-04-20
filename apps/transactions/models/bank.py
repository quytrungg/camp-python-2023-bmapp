from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel


class Bank(BaseModel):
    """Create model for Bank.

    Attrs:
        name: name of the bank, must be created by admin
        logo: an url of a bank logo image

    """

    name = models.CharField(
        verbose_name=_("Bank"),
        max_length=20,
    )
    code = models.CharField(
        verbose_name=_("Code"),
        max_length=4,
        unique=True,
        default="",
        validators=[
            RegexValidator(
                r"^[A-Z]{4}$",
                "Code must be at most 4 uppercase letters.",
            ),
        ],
    )
    logo = models.ImageField(
        verbose_name=_("Bank Logo"),
        null=False,
    )

    class Meta:
        verbose_name = _("Bank")
        verbose_name_plural = _("Banks")

    def __str__(self) -> str:
        return self.name

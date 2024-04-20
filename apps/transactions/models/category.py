from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel
from apps.users.models import User


class Category(BaseModel):
    """Create model for Category.

    Attrs:
        name: name of the category
        is_income: indicate whether this category is an income/expense
        user: user's id, indicate the user who created this category

    """

    name = models.CharField(
        verbose_name=_("Category"),
        max_length=20,
    )
    is_income = models.BooleanField(
        verbose_name=_("Income"),
        default=False,
    )
    user = models.ForeignKey(
        to=User,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        null=True,
    )

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self) -> str:
        return self.name

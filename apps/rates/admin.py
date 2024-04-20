from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ..core.admin import BaseAdmin
from .models import Currency


@admin.register(Currency)
class CurrencyAdmin(BaseAdmin):
    """UI for Currency model."""

    ordering = ("code", "name")
    list_display = (
        "name",
        "code",
    )
    list_display_links = (
        "name",
        "code",
    )
    search_fields = (
        "name",
        "code",
    )
    add_fieldsets = (
        (
            None, {
                "classes": ("wide",),
                "fields": ("name", "code"),
            },
        ),
    )
    fieldsets = (
        (
            _("Currency information"), {
                "fields": (
                    "name",
                    "code",
                ),
            },
        ),
    )

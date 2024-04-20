from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RatesConfig(AppConfig):
    """Default configuration for Users app."""

    name = "apps.rates"
    verbose_name = _("Rates")

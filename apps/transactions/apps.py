from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TransactionsConfig(AppConfig):
    """Default configuration for Transactions app."""

    name = "apps.transactions"
    verbose_name = _("Transactions")

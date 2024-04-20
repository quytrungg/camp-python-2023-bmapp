from django.db import models


class CurrencyName(models.TextChoices):
    """List of currency names for default."""

    VIETNAM = "Vietnamese Dong"
    RUSSIA = "Russian Ruble"
    US = "US Dollars"


class CurrencyCode(models.TextChoices):
    """List of currency codes for default."""

    VIETNAM = "VND"
    RUSSIA = "RUB"
    US = "USD"


DEFAULT_CURRENCY_NAME = CurrencyName.VIETNAM

DEFAULT_CURRENCY_CODE = CurrencyCode.VIETNAM

BASIC_CURRENCIES = [
    {
        "name": "Vietnamese Dong",
        "code": "VND",
    },
    {
        "name": "Russian Ruble",
        "code": "RUB",
    },
    {
        "name": "US Dollar",
        "code": "USD",
    },
    {
        "name": "Chinese Yuan",
        "code": "CNY",
    },
    {
        "name": "Japanese Yen",
        "code": "JPY",
    },
    {
        "name": "South Korean Won",
        "code": "KRW",
    },
    {
        "name": "Great British Pound",
        "code": "GBP",
    },
    {
        "name": "Euro",
        "code": "EUR",
    },
]

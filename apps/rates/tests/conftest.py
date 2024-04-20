from decimal import Decimal
from typing import Any

import pytest

from apps.rates.factories import ExchangeRateFactory
from apps.rates.models import Currency, ExchangeRate
from apps.users.models import User


@pytest.fixture
def exchange_rate_valid_data(
    first_currency: Currency,
    last_currency: Currency,
) -> dict[str, Any]:
    """Return valid data for creating a new exchange rate."""
    return {
        "source_currency": first_currency.pk,
        "destination_currency": last_currency.pk,
        "rate": Decimal(1.5),
    }


@pytest.fixture
def exchange_rate(
    exchange_rate_valid_data: dict[str, Any],
    normal_user: User,
) -> ExchangeRate:
    """Create a mock exchange rate."""
    return ExchangeRateFactory(
        user=normal_user,
        source_currency_id=exchange_rate_valid_data["source_currency"],
        destination_currency_id=(
            exchange_rate_valid_data["destination_currency"]
        ),
        rate=exchange_rate_valid_data["rate"],
    )

import pytest
from datetime import date, datetime, timezone
from decimal import Decimal
from app import api
from app.support.errors import DomainError


def code(expected, operation):
    with pytest.raises(DomainError) as caught:
        operation()
    assert caught.value.code == expected

from app.domain.fx import ExchangeRate
from app.domain.providers import TableRateProvider, FixedRateProvider
from app.support.types import money

@pytest.mark.parametrize("factory", [lambda rate: TableRateProvider({("USD", "EUR"): rate}), FixedRateProvider])
def test_progression_provider_success_missing_success(factory):
    rate = ExchangeRate("USD", "EUR", Decimal("0.9"))
    provider = factory(rate)
    assert provider.get_rate("USD", "EUR") is rate
    code("RATE_NOT_FOUND", lambda: provider.get_rate("EUR", "USD"))
    assert provider.get_rate("USD", "EUR") is rate

def test_progression_conversion_does_not_change_amount():
    amount = money("0.05", "USD")
    service = api.create(rates={("USD", "EUR"): ExchangeRate("USD", "EUR", Decimal("0.9"))})
    first = service.convert(amount, "EUR")
    code("INVALID_CURRENCY", lambda: service.convert(amount, "GBP"))
    assert service.convert(amount, "EUR") == first == money("0.05")
    assert amount == money("0.05", "USD")

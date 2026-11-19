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

from app.domain.providers import ExchangeRateProvider

def test_progression_false_provider_error_then_success():
    calls = []
    class Once(ExchangeRateProvider):
        def __bool__(self): return False
        def get_rate(self, source, target):
            calls.append((source, target))
            if len(calls) == 1: raise DomainError("TEMPORARY")
            return ExchangeRate(source, target, Decimal("0.5"))
    service = api.create(provider=Once())
    amount = money("10", "USD")
    code("TEMPORARY", lambda: service.convert(amount, "EUR"))
    assert calls == [("USD", "EUR")]
    assert service.convert(amount, "EUR") == money("5") and len(calls) == 2
    assert amount == money("10", "USD")

from app.services.fx_service import FxService
from app.support.types import money

def test_progression_extra_lab05(monkeypatch):
    calls = []
    def convert(self, amount, target):
        calls.append(target)
        if target == "GBP":
            raise DomainError("RATE_NOT_FOUND")
        return money("20", target)
    monkeypatch.setattr(FxService, "convert", convert)
    service = object.__new__(FxService)
    assert service.convert_many(money("10"), ("USD", "EUR")) == (("USD", money("20", "USD")), ("EUR", money("20")))
    assert service.available_quotes(money("10"), ("USD", "GBP", "USD")) == {"USD": money("20", "USD")}
    assert calls == ["USD", "EUR", "USD", "GBP"]

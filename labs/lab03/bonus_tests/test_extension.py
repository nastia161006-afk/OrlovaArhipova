from app import api
from app.support.errors import DomainError
from app.support.types import money
from decimal import Decimal
import pytest

def error(code, action):
    with pytest.raises(DomainError) as exc:
        action()
    assert exc.value.code == code

from app.domain import providers
from app.domain.fx import ExchangeRate

def fallback_type():
    assert hasattr(providers, "FallbackRateProvider"), "Реализуйте бонусный FallbackRateProvider"
    assert issubclass(providers.FallbackRateProvider, providers.ExchangeRateProvider)
    return providers.FallbackRateProvider

class InstrumentedProvider(providers.ExchangeRateProvider):
    def __init__(self, name, calls, response):
        self.name, self.calls, self.response = name, calls, response
    def get_rate(self, source, target):
        self.calls.append((self.name, source, target))
        if isinstance(self.response, Exception):
            raise self.response
        return self.response

def test_bonus_fallback_uses_primary_once():
    calls = []
    value = ExchangeRate("USD", "EUR", Decimal("0.5"))
    primary = InstrumentedProvider("primary", calls, value)
    fallback = InstrumentedProvider("fallback", calls, DomainError("MUST_NOT_CALL"))
    provider = fallback_type()(primary, fallback)
    assert provider.get_rate("USD", "EUR") is value
    assert calls == [("primary", "USD", "EUR")]

def test_bonus_fallback_only_when_rate_missing():
    calls = []
    value = ExchangeRate("USD", "EUR", Decimal("0.8"))
    primary = InstrumentedProvider("primary", calls, DomainError("RATE_NOT_FOUND"))
    fallback = InstrumentedProvider("fallback", calls, value)
    provider = fallback_type()(primary, fallback)
    assert provider.get_rate("USD", "EUR") is value
    assert calls == [("primary", "USD", "EUR"), ("fallback", "USD", "EUR")]

@pytest.mark.parametrize("problem,code", [
    (DomainError("UPSTREAM_FAILURE"), "UPSTREAM_FAILURE"),
    (None, "INVALID_RATE_PAIR"),
    (ExchangeRate("EUR", "USD", Decimal("2")), "INVALID_RATE_PAIR"),
])
def test_bonus_primary_problem_is_not_absence(problem, code):
    calls = []
    provider = fallback_type()(InstrumentedProvider("primary", calls, problem),
                               InstrumentedProvider("fallback", calls, None))
    error(code, lambda: provider.get_rate("USD", "EUR"))
    assert calls == [("primary", "USD", "EUR")]

@pytest.mark.parametrize("problem,code", [
    (DomainError("RATE_NOT_FOUND"), "RATE_NOT_FOUND"),
    (DomainError("UPSTREAM_FAILURE"), "UPSTREAM_FAILURE"),
    (None, "INVALID_RATE_PAIR"),
])
def test_bonus_fallback_result_and_errors_are_checked(problem, code):
    calls = []
    provider = fallback_type()(InstrumentedProvider("primary", calls, DomainError("RATE_NOT_FOUND")),
                               InstrumentedProvider("fallback", calls, problem))
    error(code, lambda: provider.get_rate("USD", "EUR"))
    assert len(calls) == 2

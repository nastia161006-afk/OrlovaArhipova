import pytest
from decimal import Decimal
from datetime import date, datetime, timezone, timedelta
from app import api
from app.support.errors import DomainError
from app.support.types import Repository, CheckResult, Money, money


def error(code, operation):
    with pytest.raises(DomainError) as caught:
        operation()
    assert caught.value.code == code


def invoke(service, method, *args, **kwargs):
    return api.call(service, method, *args, **kwargs)

def test_legacy_rates():
    from app.domain.adapters import LegacyRatesAdapter
    class Legacy:
        def lookup(self,pair):return Decimal("0.5") if pair=="USD/EUR" else None
    adapter=LegacyRatesAdapter(Legacy())
    assert adapter.get_rate("USD","EUR").rate==Decimal("0.5")
    error("RATE_NOT_FOUND",lambda:adapter.get_rate("EUR","USD"))

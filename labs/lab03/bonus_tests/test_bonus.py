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

def test_table_copies_configuration():
    from app.domain.fx import ExchangeRate
    from app.domain.providers import TableRateProvider
    rates={("USD","EUR"):ExchangeRate("USD","EUR",Decimal("1"))}
    provider=TableRateProvider(rates)
    rates.clear()
    assert provider.get_rate("USD","EUR").rate==1

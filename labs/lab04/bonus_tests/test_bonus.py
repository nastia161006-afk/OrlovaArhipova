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

def test_pair_diagnostic_delegates(monkeypatch):
    from app.domain.fx import ExchangeRate
    rate=ExchangeRate("USD","EUR",Decimal("1"))
    calls=[]
    def matches(self,*args):
        calls.append(args)
        return True
    monkeypatch.setattr(ExchangeRate,"matches",matches)
    assert api.create().pair_matches(rate,"USD","EUR")
    assert len(calls)==1

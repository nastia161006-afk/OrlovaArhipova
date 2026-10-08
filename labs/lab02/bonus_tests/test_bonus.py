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

def test_very_small_rate():
    rate=api.make("USD","EUR",Decimal("0.0001"))
    service=api.create(rates={("USD","EUR"):rate})
    assert invoke(service,"convert",money("1","USD"),"EUR")==money("0")

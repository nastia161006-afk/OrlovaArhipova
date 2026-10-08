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

def rate(value="0.85",source="USD",target="EUR"):
    return api.make(source,target,Decimal(value))

@pytest.mark.parametrize("amount,expected",[("100","85"),("10","8.50"),("0","0")])
def test_conversion(amount,expected):
    original=money(amount,"USD")
    assert invoke(api.create(),"convert",original,"EUR")==money(expected)
    assert original==money(amount,"USD")

def test_two_tables_do_not_affect_each_other():
    first=api.create(rates={("USD","EUR"):rate("0.85")})
    second=api.create(rates={("USD","EUR"):rate("0.80")})
    assert invoke(first,"convert",money("100","USD"),"EUR")==money("85")
    assert invoke(second,"convert",money("100","USD"),"EUR")==money("80")

def test_identity_and_missing_rate():
    empty=api.create(rates={})
    assert invoke(empty,"convert",money("10"),"EUR")==money("10")
    error("RATE_NOT_FOUND",lambda:invoke(empty,"convert",money("1","USD"),"EUR"))

@pytest.mark.parametrize("value",["0","-1","NaN","Infinity"])
def test_invalid_rate(value):
    error("INVALID_RATE",lambda:rate(value))

def test_same_currency_is_not_an_exchange_pair():
    error("INVALID_RATE_PAIR",lambda:rate("1","EUR","EUR"))

def test_half_up_rounding_of_result_only():
    service=api.create(rates={("USD","EUR"):rate("0.9")})
    assert invoke(service,"convert",money("0.05","USD"),"EUR")==money("0.05")

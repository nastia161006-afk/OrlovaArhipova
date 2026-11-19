import pytest
from decimal import Decimal
from datetime import date, datetime, timezone, timedelta
from app import api
from app.support.errors import DomainError


def assert_code(code, action):
    with pytest.raises(DomainError) as caught:
        action()
    assert caught.value.code == code

from app.support.types import money

def test_review_rate_precision_not_money_precision():
    rate=api.make("USD","EUR",Decimal("0.85555"))
    service=api.create(rates={("USD","EUR"):rate})
    assert api.call(service,"convert",money("100","USD"),"EUR") == money("85.56")
    assert rate.rate == Decimal("0.85555")

def test_review_none_is_not_a_valid_rate():
    from app.domain.providers import ExchangeRateProvider
    from app.services.fx_service import FxService
    class Wrong(ExchangeRateProvider):
        def get_rate(self,source,target):return None
    assert_code("INVALID_RATE_PAIR",lambda:FxService(Wrong()).convert(money("1","USD"),"EUR"))

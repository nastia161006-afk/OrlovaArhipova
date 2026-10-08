from app import api
from app.support.errors import DomainError
from app.support.types import money
from decimal import Decimal
import pytest

def error(code, action):
    with pytest.raises(DomainError) as exc:
        action()
    assert exc.value.code == code

from app.domain.fx import ExchangeRate
from decimal import localcontext

@pytest.mark.parametrize("value,expected", [("2", "0.5"), ("4", "0.25"), ("0.0001", "10000")])
def test_bonus_inverse_is_a_new_value(value, expected):
    rate = ExchangeRate("USD", "EUR", Decimal(value))
    assert hasattr(rate, "inverse"), "Реализуйте бонусный метод inverse"
    inverse = rate.inverse()
    assert isinstance(inverse, ExchangeRate) and inverse is not rate
    assert (inverse.source, inverse.target, inverse.rate) == ("EUR", "USD", Decimal(expected))
    assert (rate.source, rate.target, rate.rate) == ("USD", "EUR", Decimal(value))

def test_bonus_inverse_keeps_local_decimal_precision():
    rate = ExchangeRate("USD", "EUR", Decimal("3"))
    assert hasattr(rate, "inverse"), "Реализуйте бонусный метод inverse"
    with localcontext() as context:
        context.prec = 3
        assert rate.inverse().rate == Decimal("0.3333333333333333333333333333")
        assert context.prec == 3

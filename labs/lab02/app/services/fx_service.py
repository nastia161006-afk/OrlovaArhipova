from decimal import ROUND_HALF_UP
from app.support.types import Money
from decimal import Decimal, localcontext
from app.domain.fx import ExchangeRate
from app.support.types import currency, rounded_money
from app.support.errors import DomainError


class FxService:
    def __init__(self, rates):
        self._rates = dict(rates)

    def convert(self, amount, target_currency):
        currency(target_currency)
        
        # 1. Если валюты одинаковые — возвращаем исходную сумму (Шаг 3)
        if amount.currency == target_currency:
            return amount
            
        # 2. Если пары нет — выбрасываем ошибку (Шаг 3)
        if (amount.currency, target_currency) not in self._rates:
            raise DomainError("RATE_NOT_FOUND")
            
        rate = self._rates[(amount.currency, target_currency)]
        
        # 3. Умножаем точно, округляем только итог по HALF_UP (Шаг 2)
        with localcontext() as ctx:
            ctx.prec = 28
            converted_amount = amount.amount * rate.rate
            rounded_value = converted_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            return Money(rounded_value, target_currency)


def make_entity(*args, **kwargs):
    return ExchangeRate(*args, **kwargs)


def invoke(service, method, *args, **kwargs):
    return getattr(service, method)(*args, **kwargs)


def view(entity):
    return {'source': entity.source, 'target': entity.target, 'rate': entity.rate}


from decimal import Decimal

def new_service(rates=None):
    rates = {("USD","EUR"): make_entity("USD","EUR",Decimal("0.85"))} if rates is None else rates
    return FxService(rates)
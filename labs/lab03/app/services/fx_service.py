from decimal import Decimal, localcontext
from app.domain.fx import ExchangeRate
from app.support.types import currency, rounded_money
from app.support.errors import DomainError


class FxService:
    def __init__(self, rates):
        self._rates = dict(rates)

    def convert(self, amount, target_currency):
        raise NotImplementedError("ЛР3: реализуйте FxService.convert по TASK.md")

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

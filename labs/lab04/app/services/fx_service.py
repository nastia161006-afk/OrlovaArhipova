from decimal import Decimal, localcontext
from app.domain.fx import ExchangeRate
from app.domain.providers import TableRateProvider
from app.support.types import currency, rounded_money
from app.support.errors import DomainError

class FxService:
    def __init__(self, provider):
        self._provider = provider

    def convert(self, amount, target_currency):
        currency(target_currency)
        
        if amount.currency == target_currency:
            return amount

        exchange_rate = self._provider.get_rate(amount.currency, target_currency)

        if not isinstance(exchange_rate, ExchangeRate) or not exchange_rate.matches(amount.currency, target_currency):
            raise DomainError("INVALID_RATE_PAIR")

        with localcontext() as ctx:
            ctx.prec = 28
            converted_amount = amount.amount * exchange_rate.rate

        return rounded_money(converted_amount, target_currency)

def make_entity(*args, **kwargs):
    return ExchangeRate(*args, **kwargs)

def invoke(service, method, *args, **kwargs):
    return getattr(service, method)(*args, **kwargs)

def view(entity):
    return {'source': entity.source, 'target': entity.target, 'rate': entity.rate}

def new_service(provider=None, rates=None):
    if rates is None:
        rates = {("USD","EUR"): make_entity("USD","EUR",Decimal("0.85"))}
    if provider is None:
        provider = TableRateProvider(rates)
    return FxService(provider)
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
        if isinstance(self._provider, TableRateProvider):
            pair = (amount.currency, target_currency)
            if pair not in self._provider._rates:
                raise DomainError("RATE_NOT_FOUND")
            rate = self._provider._rates[pair]
        else:
            rate = self._provider.get_rate(amount.currency, target_currency)
        if not isinstance(rate, ExchangeRate) or not rate.matches(amount.currency, target_currency):
            raise DomainError("INVALID_RATE_PAIR")
        with localcontext() as ctx:
            ctx.prec = 28
            if isinstance(self._provider, TableRateProvider):
                return rounded_money(amount.amount * rate.rate, target_currency)
            return rounded_money(amount.amount * rate.rate, target_currency)

    def pair_matches(self,rate,source,target):
        return rate.source==source and rate.target==target

def make_entity(*args, **kwargs):
    return ExchangeRate(*args, **kwargs)


def invoke(service, method, *args, **kwargs):
    return getattr(service, method)(*args, **kwargs)


def view(entity):
    return {'source': entity.source, 'target': entity.target, 'rate': entity.rate}


from decimal import Decimal
from app.domain.providers import TableRateProvider

def new_service(provider=None, rates=None):
    rates = {("USD","EUR"): make_entity("USD","EUR",Decimal("0.85"))} if rates is None else rates
    if provider is None:
        provider = TableRateProvider(rates)
    return FxService(provider)

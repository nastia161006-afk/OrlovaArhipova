from decimal import Decimal, localcontext

from app.domain.fx import ExchangeRate
from app.support.errors import DomainError
from app.support.types import currency, rounded_money


class FxService:
    def __init__(self, rates):
        self._rates = dict(rates)

    def convert(self, amount, target_currency):
        currency(target_currency)

        if amount.currency == target_currency:
            return amount

        pair = (amount.currency, target_currency)

        if pair not in self._rates:
            raise DomainError("RATE_NOT_FOUND")

        exchange_rate = self._rates[pair]

        if (
            not isinstance(exchange_rate, ExchangeRate)
            or exchange_rate.source != amount.currency
            or exchange_rate.target != target_currency
        ):
            raise DomainError("INVALID_RATE_PAIR")

        with localcontext() as ctx:
            ctx.prec = 28
            converted_amount = amount.amount * exchange_rate.rate

        return rounded_money(converted_amount, target_currency)


def make_entity(source, target, rate):
    return ExchangeRate(source, target, rate)


def view(rate):
    return {
        "source": rate.source,
        "target": rate.target,
        "rate": rate.rate,
    }


def invoke(service, method, amount, target_currency):
    if method != "convert":
        raise ValueError(method)

    return service.convert(amount, target_currency)


def new_service(rates=None):
    if rates is None:
        rates = {
            ("USD", "EUR"): ExchangeRate(
                "USD",
                "EUR",
                Decimal("0.85"),
            )
        }

    return FxService(rates)

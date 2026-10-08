from decimal import Decimal, localcontext

from app.domain.fx import ExchangeRate
from app.support.errors import DomainError
from app.support.types import currency, rounded_money


class FxService:
    def __init__(self, rates): # словарь с курсами
        self._rates = dict(rates) # копируем, чтобы не менять оригинал

    def convert(self, amount, target_currency):
        currency(target_currency) # проверяем, что валюта верная

        if amount.currency == target_currency:
            return amount # если валюты одинаковые — просто возвращаем сумму

        pair = (amount.currency, target_currency) # пара для поиска

        if pair not in self._rates:
            raise DomainError("RATE_NOT_FOUND") # нет курса для такой пары

        exchange_rate = self._rates[pair]

        if (
            not isinstance(exchange_rate, ExchangeRate) # проверка объекта
            or exchange_rate.source != amount.currency # откуда
            or exchange_rate.target != target_currency # куда
        ):
            raise DomainError("INVALID_RATE_PAIR")

        with localcontext() as ctx: # умножаем сумму на курс
            ctx.prec = 28
            converted_amount = amount.amount * exchange_rate.rate

        return rounded_money(converted_amount, target_currency)


def make_entity(source, target, rate): # объект курса валют
    return ExchangeRate(source, target, rate)


def view(rate): # превращение обратно в словарь
    return {
        "source": rate.source,
        "target": rate.target,
        "rate": rate.rate,
    }


def invoke(service, method, amount, target_currency): # API заходит в сервис
    if method != "convert":
        raise ValueError(method)

    return service.convert(amount, target_currency)


def new_service(rates=None): # создает сервис с курсом
    if rates is None:
        rates = {
            ("USD", "EUR"): ExchangeRate(
                "USD",
                "EUR",
                Decimal("0.85"),
            )
        }

    return FxService(rates)

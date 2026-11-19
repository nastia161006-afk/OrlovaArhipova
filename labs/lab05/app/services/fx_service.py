from decimal import Decimal, localcontext
from app.domain.fx import ExchangeRate
from app.domain.providers import TableRateProvider
from app.support.types import currency, rounded_money
from app.support.errors import DomainError

class FxService:
    def __init__(self, provider):
        # Проверка именно на None (Шаг 3 задания)
        if provider is None:
            raise ValueError("Provider cannot be None")
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

    def convert_many(self, amount, target_currencies):
        return tuple(
            (curr, self.convert(amount, curr)) for curr in target_currencies
        )

    def available_quotes(self, amount, target_currencies):
        quotes = {}
        for curr in target_currencies:
            # Пропускаем, если уже есть в словаре (чтобы не вызывать повторно)
            if curr in quotes:
                continue
            
            try:
                # ВАЖНО: используем self.convert, а не self._provider
                converted_amount = self.convert(amount, curr)
                quotes[curr] = converted_amount
            except DomainError as e:
                # Используем e.code для проверки ошибки
                if getattr(e, 'code', '') == "RATE_NOT_FOUND":
                    continue
                # Остальные ошибки (например, TEMPORARY) пробрасываем наружу
                raise
                
        return quotes

def make_entity(*args, **kwargs):
    return ExchangeRate(*args, **kwargs)

def invoke(service, method, *args, **kwargs):
    return getattr(service, method)(*args, **kwargs)

def view(entity):
    return {'source': entity.source, 'target': entity.target, 'rate': entity.rate}
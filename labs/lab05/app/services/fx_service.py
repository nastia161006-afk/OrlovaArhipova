from decimal import Decimal, localcontext
from app.domain.fx import ExchangeRate
from app.domain.providers import TableRateProvider
from app.support.types import currency, rounded_money
from app.support.errors import DomainError


class FxService:
    # Сервис конвертации, который принимает зависимость (провайдера) извне
    def __init__(self, provider):
        # Проверяем, что провайдер не равен None (защита от отсутствия зависимости)
        if provider is None:
            raise ValueError("Provider cannot be None")
        # Сохраняем переданный объект для дальнейшего использования
        self._provider = provider

    def convert(self, amount, target_currency):
        # Проверяем корректность целевой валюты
        currency(target_currency)

        # Если валюты совпадают, возвращаем исходную сумму без поиска курса
        if amount.currency == target_currency:
            return amount

        # Получаем курс у провайдера (полиморфный вызов)
        exchange_rate = self._provider.get_rate(amount.currency, target_currency)

        # Проверяем, что вернулся правильный объект и верное направление пары
        if not isinstance(exchange_rate, ExchangeRate) or not exchange_rate.matches(amount.currency, target_currency):
            raise DomainError("INVALID_RATE_PAIR")

        # Выполняем умножение с высокой точностью (без промежуточного округления)
        with localcontext() as ctx:
            ctx.prec = 28
            converted_amount = amount.amount * exchange_rate.rate

        # Округляем только итоговый денежный результат
        return rounded_money(converted_amount, target_currency)

    def convert_many(self, amount, target_currencies):
        # Возвращаем кортеж из пар (валюта, новая сумма), вызывая convert для каждой валюты
        return tuple(
            (curr, self.convert(amount, curr)) for curr in target_currencies
        )

    def available_quotes(self, amount, target_currencies):
        # Словарь для хранения доступных курсов (целевая валюта -> сконвертированная сумма)
        quotes = {}

        for curr in target_currencies:
            # Пропускаем дубликаты, если валюта уже обработана (оптимизация)
            if curr in quotes:
                continue

            try:
                # Используем метод convert для получения результата
                converted_amount = self.convert(amount, curr)
                quotes[curr] = converted_amount
            except DomainError as e:
                # Если курс не найден — просто пропускаем эту валюту
                if getattr(e, 'code', '') == "RATE_NOT_FOUND":
                    continue
                # Все остальные ошибки (например, отказ источника) пробрасываем наружу
                raise

        return quotes


def make_entity(*args, **kwargs):
    # Вспомогательная функция для создания объекта курса
    return ExchangeRate(*args, **kwargs)


def invoke(service, method, *args, **kwargs):
    # Универсальный вызов метода сервиса по имени (для API и тестов)
    return getattr(service, method)(*args, **kwargs)


def view(entity):
    # Превращает объект в словарь (для сериализации)
    return {'source': entity.source, 'target': entity.target, 'rate': entity.rate}
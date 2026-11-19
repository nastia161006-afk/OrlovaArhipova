from decimal import Decimal, localcontext  # Для точных вычислений и управления контекстом
from app.domain.fx import ExchangeRate  # Класс валютного курса
from app.domain.providers import ExchangeRateProvider, TableRateProvider  # Абстрактный интерфейс и табличный провайдер
from app.support.types import currency, rounded_money  # Функции проверки валюты и округления денег
from app.support.errors import DomainError  # Ошибки предметной области


class FxService:  # Сервис конвертации валют

    # Внедряем зависимость (провайдера) через конструктор
    def __init__(self, provider: ExchangeRateProvider):  # Аннотация типа: ждем наследника ExchangeRateProvider
        self._provider = provider  # Сохраняем провайдера для дальнейшего использования

    def convert(self, amount, target_currency):  # Основной метод конвертации
        # Проверяем, что целевая валюта корректна (например, USD, EUR)
        currency(target_currency)

        # При совпадении валют возвращаем исходную сумму без поиска курса (оптимизация)
        if amount.currency == target_currency:
            return amount

        # Получаем курс через провайдера. Сервис не знает, таблица это или фикс. (Полиморфизм)
        exchange_rate = self._provider.get_rate(amount.currency, target_currency)

        # Проверяем, что нам вернули именно объект ExchangeRate и правильное направление пары
        if (
            not isinstance(exchange_rate, ExchangeRate)  # Защита от "плохих" провайдеров
            or exchange_rate.source != amount.currency  # Проверка исходной валюты
            or exchange_rate.target != target_currency  # Проверка целевой валюты
        ):
            raise DomainError("INVALID_RATE_PAIR")  # Ошибка, если пара не совпадает

        # Умножаем сумму на курс, используя контекст высокой точности (28 знаков)
        with localcontext() as ctx:  # Открываем локальный контекст для вычислений
            ctx.prec = 28  # Устанавливаем точность, чтобы не потерять копейки
            converted_amount = amount.amount * exchange_rate.rate  # Умножаем

        # Округляем только итоговый денежный результат и возвращаем в нужной валюте
        return rounded_money(converted_amount, target_currency)


def make_entity(*args, **kwargs):  # Создает объект курса
    return ExchangeRate(*args, **kwargs)  # Пробрасываем аргументы в конструктор ExchangeRate

def invoke(service, method, *args, **kwargs):  # Универсальный вызов метода у сервиса
    return getattr(service, method)(*args, **kwargs)  # Вызываем метод по имени (например, 'convert')

def view(entity):  # Превращает объект курса в словарь (для сериализации в JSON)
    return {'source': entity.source, 'target': entity.target, 'rate': entity.rate}  # Возвращаем dict


def new_service(rates=None):  # Функция создания сервиса
    # Если курсы не переданы, создаем дефолтный словарь с курсом USD/EUR
    rates = {("USD","EUR"): make_entity("USD","EUR",Decimal("0.85"))} if rates is None else rates
    
    # Оборачиваем словарь в TableRateProvider и передаем в FxService (Внедрение зависимости)
    return FxService(TableRateProvider(rates))  # Возвращаем готовый к работе сервис
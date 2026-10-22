from decimal import ROUND_HALF_UP  # Правило округления
from app.support.types import Money  # Денежная сумма
from decimal import Decimal, localcontext  # Точные вычисления
from app.domain.fx import ExchangeRate  # Курс валют
from app.support.types import currency, rounded_money  # Работа с валютами
from app.support.errors import DomainError  # Ошибки предметной области


class FxService:  # Сервис конвертации валют

    def __init__(self, rates):  # Инициализация сервиса
        self._rates = dict(rates)  # Сохраняем курсы валют

    def convert(self, amount, target_currency):  # Конвертация суммы
        currency(target_currency)  # Проверяем целевую валюту

        # Если валюты совпадают, возвращаем исходную сумму
        if amount.currency == target_currency:
            return amount

        # Проверяем наличие курса
        if (amount.currency, target_currency) not in self._rates:
            raise DomainError("RATE_NOT_FOUND")  # Ошибка отсутствующего курса

        rate = self._rates[(amount.currency, target_currency)]  # Получаем курс

        # Настраиваем точность вычислений
        with localcontext() as ctx:
            ctx.prec = 28  # Устанавливаем точность

            converted_amount = amount.amount * rate.rate  # Умножаем на курс

            # Округляем результат до двух знаков
            rounded_value = converted_amount.quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

            return Money(rounded_value, target_currency)  # Возвращаем результат


def make_entity(*args, **kwargs):  # Создание объекта курса
    return ExchangeRate(*args, **kwargs)  # Возвращаем курс


def invoke(service, method, *args, **kwargs):  # Вызов метода по имени
    return getattr(service, method)(*args, **kwargs)  # Выполняем вызов


def view(entity):  # Представление курса в виде словаря
    return {
        'source': entity.source,  # Исходная валюта
        'target': entity.target,  # Целевая валюта
        'rate': entity.rate       # Значение курса
    }


from decimal import Decimal  # Импорт Decimal (повторный)


def new_service(rates=None):  # Создание сервиса
    # Используем стандартный курс, если другие не переданы
    rates = {
        ("USD", "EUR"): make_entity("USD", "EUR", Decimal("0.85"))
    } if rates is None else rates

    return FxService(rates)  # Возвращаем готовый сервис
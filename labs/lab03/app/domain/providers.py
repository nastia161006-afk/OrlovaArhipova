from abc import ABC, abstractmethod  # Для абстрактных классов
from decimal import Decimal, localcontext  # Для точных вычислений
from app.domain.fx import ExchangeRate  # Класс валютного курса
from app.support.errors import DomainError  # Ошибки предметной области

class ExchangeRateProvider(ABC):  # Общий интерфейс поставщика курсов

    @abstractmethod  # Обязательный для реализации метод
    def get_rate(self, source, target):  # Получение курса валют
        pass  # Реализация в дочерних классах

class TableRateProvider(ExchangeRateProvider):  # Поставщик нескольких курсов

    def __init__(self, rates):  # Принимаем словарь курсов
        self._rates = dict(rates)  # Сохраняем курсы в словаре

        for pair, rate in self._rates.items():  # Перебираем все курсы
            # Проверяем тип курса и соответствие пары валют
            if not isinstance(rate, ExchangeRate) or pair != (rate.source, rate.target):
                raise DomainError("INVALID_RATE_PAIR")  # Ошибка пары валют

    def get_rate(self, source, target):  # Ищем курс по двум валютам
        if (source, target) not in self._rates:  # Проверяем наличие курса
            raise DomainError("RATE_NOT_FOUND")  # Курс не найден
        return self._rates[(source, target)]  # Возвращаем найденный курс

class FixedRateProvider(ExchangeRateProvider):  # Поставщик одного курса

    def __init__(self, exchange_rate):  # Принимаем один курс
        if not isinstance(exchange_rate, ExchangeRate):  # Проверяем тип объекта
            raise DomainError("INVALID_RATE")  # Некорректный курс
        self._rate = exchange_rate  # Сохраняем курс

    def get_rate(self, source, target):  # Получаем курс по валютам
        if not self._rate.matches(source, target):  # Проверяем совпадение валют
            raise DomainError("RATE_NOT_FOUND")  # Курс не найден
        return self._rate  # Возвращаем сохранённый курс
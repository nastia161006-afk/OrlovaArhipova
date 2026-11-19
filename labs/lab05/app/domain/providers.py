from abc import ABC, abstractmethod
from app.domain.fx import ExchangeRate
from app.support.errors import DomainError


class ExchangeRateProvider(ABC):
    # Абстрактный класс, задающий общий интерфейс для всех источников курсов
    @abstractmethod
    def get_rate(self, source, target):
        # Обязательный метод для всех наследников (возвращает объект ExchangeRate)
        raise NotImplementedError


class TableRateProvider(ExchangeRateProvider):
    # Провайдер, который хранит курсы в виде словаря (таблицы)
    def __init__(self, rates):
        # Делаем независимую копию словаря, чтобы внешние изменения не влияли на провайдера
        self._rates = dict(rates)

        # Валидация: проверяем, что в словаре лежат правильные объекты с совпадающими ключами
        for pair, rate in self._rates.items():
            if not isinstance(rate, ExchangeRate) or pair != (rate.source, rate.target):
                raise DomainError("INVALID_RATE_PAIR")

    def get_rate(self, source, target):
        # Проверяем наличие запрошенной пары в нашей таблице
        if (source, target) not in self._rates:
            raise DomainError("RATE_NOT_FOUND")
        # Возвращаем найденный объект курса
        return self._rates[(source, target)]


class FixedRateProvider(ExchangeRateProvider):
    # Провайдер, который хранит только один фиксированный курс
    def __init__(self, exchange_rate):
        # Проверяем, что передан именно объект курса
        if not isinstance(exchange_rate, ExchangeRate):
            raise DomainError("INVALID_RATE")
        self._rate = exchange_rate

    def get_rate(self, source, target):
        # Проверяем, совпадает ли запрос с нашим единственным курсом
        if not self._rate.matches(source, target):
            raise DomainError("RATE_NOT_FOUND")
        # Возвращаем сохраненный курс
        return self._rate
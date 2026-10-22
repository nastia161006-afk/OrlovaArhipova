from abc import ABC, abstractmethod
from decimal import Decimal, localcontext
from app.domain.fx import ExchangeRate
from app.support.errors import DomainError


class ExchangeRateProvider(ABC):
    @abstractmethod
    def get_rate(self, source, target):
        pass


class TableRateProvider(ExchangeRateProvider):
    def __init__(self, rates):
        self._rates = dict(rates)
        for pair, rate in self._rates.items():
            if not isinstance(rate, ExchangeRate) or pair != (rate.source, rate.target):
                raise DomainError("INVALID_RATE_PAIR")

    def get_rate(self, source, target):
        if (source, target) not in self._rates:
            raise DomainError("RATE_NOT_FOUND")
        return self._rates[(source, target)]


class FixedRateProvider(ExchangeRateProvider):
    def __init__(self, exchange_rate):
        if not isinstance(exchange_rate, ExchangeRate):
            raise DomainError("INVALID_RATE")
        self._rate = exchange_rate

    def get_rate(self, source, target):
        if not self._rate.matches(source, target):
            raise DomainError("RATE_NOT_FOUND")
        return self._rate
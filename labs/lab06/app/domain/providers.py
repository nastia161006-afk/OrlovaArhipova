from abc import ABC, abstractmethod
from decimal import Decimal, localcontext
from app.domain.fx import ExchangeRate
from app.support.errors import DomainError


class ExchangeRateProvider(ABC):
    @abstractmethod
    def get_rate(self, source, target):
        raise NotImplementedError


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


class ReverseRateProvider(ExchangeRateProvider):
    def __init__(self, base_provider, allow_reverse=True):
        if not isinstance(base_provider, ExchangeRateProvider):
            raise DomainError("INVALID_CONFIG")
        if not isinstance(allow_reverse, bool):
            raise DomainError("INVALID_CONFIG")
        self.base_provider = base_provider
        self.allow_reverse = allow_reverse

    def get_rate(self, source, target):
        try:
            rate = self.base_provider.get_rate(source, target)
            if not isinstance(rate, ExchangeRate) or not rate.matches(source, target):
                raise DomainError("INVALID_RATE_PAIR")
            return rate
        except DomainError as e:
            if e.code != "RATE_NOT_FOUND":
                raise e

            if not self.allow_reverse:
                raise e

            try:
                rev = self.base_provider.get_rate(target, source)
                if not isinstance(rev, ExchangeRate) or not rev.matches(target, source):
                    raise DomainError("INVALID_RATE_PAIR")

                with localcontext() as ctx:
                    ctx.prec = 28
                    rate_val = Decimal("1") / rev.rate
                return ExchangeRate(source, target, rate_val)
            except DomainError as e2:
                raise e2


class FallbackRateProvider(ExchangeRateProvider):
    def __init__(self, primary, fallback):
        if not isinstance(primary, ExchangeRateProvider) or not isinstance(fallback, ExchangeRateProvider):
            raise DomainError("INVALID_CONFIG")
        self.primary = primary
        self.fallback = fallback

    def get_rate(self, source, target):
        try:
            rate = self.primary.get_rate(source, target)
        except DomainError as e:
            if e.code == "RATE_NOT_FOUND":
                rate = self.fallback.get_rate(source, target)
            else:
                raise e

        if not isinstance(rate, ExchangeRate) or not rate.matches(source, target):
            raise DomainError("INVALID_RATE_PAIR")

        return rate
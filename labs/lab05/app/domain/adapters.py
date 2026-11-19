from app.domain.providers import ExchangeRateProvider
from app.domain.fx import ExchangeRate
from app.support.errors import DomainError

class LegacyRatesAdapter(ExchangeRateProvider):
    def __init__(self,legacy):self._legacy=legacy
    def get_rate(self,source,target):
        raise NotImplementedError("Бонус: локальный адаптер")

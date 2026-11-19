from decimal import Decimal
from app.services.fx_service import FxService, make_entity
from app.domain.providers import TableRateProvider


def build_service(provider=None, rates=None):
    # Если курсы не переданы, создаем дефолтный словарь с курсом USD/EUR
    if rates is None:
        rates = {("USD", "EUR"): make_entity("USD", "EUR", Decimal("0.85"))}

    # Если провайдер не передан, создаем табличный провайдер на основе словаря
    if provider is None:
        provider = TableRateProvider(rates)

    # Возвращаем собранный сервис с внедренной зависимостью
    return FxService(provider)from decimal import Decimal
from app.services.fx_service import FxService, make_entity
from app.domain.providers import TableRateProvider

def build_service(provider=None, rates=None):
    # Если курсы не переданы, создаем дефолтный словарь с курсом USD/EUR
    if rates is None:
        rates = {("USD","EUR"): make_entity("USD","EUR",Decimal("0.85"))}

    # Если провайдер не передан, создаем табличный провайдер на основе словаря
    if provider is None:
        provider = TableRateProvider(rates)

    # Возвращаем собранный сервис с внедренной зависимостью
    return FxService(provider)
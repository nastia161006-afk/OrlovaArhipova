from decimal import Decimal
from app.services.fx_service import FxService, make_entity
from app.domain.providers import TableRateProvider, ReverseRateProvider


def build_service(provider=None, rates=None):
    # Если словарь курсов не передан, создаём дефолтный
    if rates is None:
        rates = {("USD", "EUR"): make_entity("USD", "EUR", Decimal("0.85"))}

    # Если не передан готовый провайдер, создаём табличный
    if provider is None:
        provider = TableRateProvider(rates)

    # Оборачиваем базовый провайдер в поиск обратного курса
    provider = ReverseRateProvider(provider)

    # Возвращаем готовый сервис
    return FxService(provider)
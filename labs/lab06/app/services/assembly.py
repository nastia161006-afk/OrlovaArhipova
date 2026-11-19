from decimal import Decimal  # Импорт типа Decimal для точных чисел
from app.services.fx_service import FxService, make_entity  # Импорт сервиса и фабричной функции
from app.domain.providers import TableRateProvider, ReverseRateProvider  # Импорт нужных провайдеров

def build_service(provider=None, rates=None):  # Функция-фабрика для сборки готового сервиса
    if rates is None:  # Проверяем, передан ли словарь курсов
        rates = {("USD","EUR"): make_entity("USD","EUR",Decimal("0.85"))}  # Если нет, создаем дефолтный словарь с курсом
    if provider is None:  # Проверяем, передан ли готовый провайдер
        provider = TableRateProvider(rates)  # Если нет, создаем табличный провайдер на основе словаря
    provider = ReverseRateProvider(provider)  # Оборачиваем базовый провайдер в поиск обратного курса
    return FxService(provider)  # Возвращаем собранный сервис с внедренными зависимостями
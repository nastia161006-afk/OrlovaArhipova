from abc import ABC, abstractmethod  # Импорт инструментов для создания абстрактных классов
from decimal import Decimal, localcontext  # Импорт Decimal для точных вычислений и контекста точности
from app.domain.fx import ExchangeRate  # Импорт класса курса валют
from app.support.errors import DomainError  # Импорт класса ошибок бизнес-логики

class ExchangeRateProvider(ABC):  # Абстрактный базовый класс (контракт для всех источников курсов)
    @abstractmethod  # Декоратор, обязывающий наследников реализовать этот метод
    def get_rate(self, source, target):  # Абстрактный метод получения курса
        """Абстрактный метод для получения курса валют."""  # Строка документации (docstring)
        raise NotImplementedError  # Заглушка: метод должен быть переопределен в дочерних классах

class TableRateProvider(ExchangeRateProvider):  # Провайдер, хранящий курсы в словаре
    def __init__(self, rates):  # Конструктор, принимает словарь с курсами
        self._rates = dict(rates)  # Создаем независимую копию словаря, чтобы внешние изменения не влияли на провайдер
        for pair, rate in self._rates.items():  # Перебираем все пары и курсы в словаре для валидации
            if not isinstance(rate, ExchangeRate) or pair != (rate.source, rate.target):  # Проверяем корректность данных: объект курса и совпадение ключа с направлением
                raise DomainError("INVALID_RATE_PAIR")  # Выбрасываем ошибку, если данные некорректны

    def get_rate(self, source, target):  # Реализация метода получения курса
        if (source, target) not in self._rates:  # Проверяем наличие запрошенной пары в таблице
            raise DomainError("RATE_NOT_FOUND")  # Выбрасываем ошибку, если пары нет
        return self._rates[(source, target)]  # Возвращаем найденный объект курса

class FixedRateProvider(ExchangeRateProvider):  # Провайдер, хранящий только один фиксированный курс
    def __init__(self, exchange_rate):  # Конструктор, принимает один объект курса
        if not isinstance(exchange_rate, ExchangeRate):  # Проверяем, что передан именно объект ExchangeRate
            raise DomainError("INVALID_RATE")  # Выбрасываем ошибку при неверном типе
        self._rate = exchange_rate  # Сохраняем курс во внутреннюю переменную

    def get_rate(self, source, target):  # Реализация метода получения курса
        if not self._rate.matches(source, target):  # Проверяем, совпадает ли запрос с нашим единственным курсом
            raise DomainError("RATE_NOT_FOUND")  # Если просят не нашу пару, выбрасываем ошибку
        return self._rate  # Возвращаем сохраненный курс

class ReverseRateProvider(ExchangeRateProvider):  # Провайдер-обертка для поиска обратного курса
    def __init__(self, base_provider, allow_reverse=True):  # Конструктор принимает базовый провайдер и флаг
        if not isinstance(base_provider, ExchangeRateProvider):  # Проверяем, что базовый провайдер является наследником интерфейса
            raise DomainError("INVALID_CONFIG")  # Ошибка конфигурации при неверном типе
        if not isinstance(allow_reverse, bool):  # Проверяем, что флаг имеет логический тип
            raise DomainError("INVALID_CONFIG")  # Ошибка конфигурации при неверном типе флага
        self.base_provider = base_provider  # Сохраняем ссылку на базовый провайдер
        self.allow_reverse = allow_reverse  # Сохраняем флаг разрешения обратного поиска

    def get_rate(self, source, target):  # Реализация метода получения курса
        try:  # Блок обработки исключений для прямого поиска
            rate = self.base_provider.get_rate(source, target)  # Пытаемся получить прямой курс у базового провайдера
            if not isinstance(rate, ExchangeRate) or not rate.matches(source, target):  # Проверяем тип и направление полученного курса
                raise DomainError("INVALID_RATE_PAIR")  # Ошибка, если курс не того направления
            return rate  # Возвращаем корректный прямой курс
        except DomainError as e:  # Перехватываем ошибки бизнес-логики от базового провайдера
            if e.code != "RATE_NOT_FOUND":  # Если ошибка не "курс не найден" (например, сбой сети)
                raise e  # Пробрасываем эту ошибку дальше без изменений
            if not self.allow_reverse:  # Если обратный поиск запрещен флагом
                raise e  # Возвращаем исходную ошибку "курс не найден"
            try:  # Блок обработки для обратного поиска
                rev = self.base_provider.get_rate(target, source)  # Запрашиваем обратную пару (target -> source)
                if not isinstance(rev, ExchangeRate) or not rev.matches(target, source):  # Проверяем корректность обратного курса
                    raise DomainError("INVALID_RATE_PAIR")  # Ошибка, если обратный курс неверного направления
                with localcontext() as ctx:  # Открываем контекст для точных вычислений
                    ctx.prec = 28  # Устанавливаем точность 28 знаков после запятой
                    rate_val = Decimal("1") / rev.rate  # Вычисляем обратный курс как 1 / rate
                return ExchangeRate(source, target, rate_val)  # Создаем и возвращаем новый объект курса
            except DomainError as e2:  # Перехватываем ошибки при обратном поиске
                raise e2  # Пробрасываем ошибку дальше

class FallbackRateProvider(ExchangeRateProvider):  # Провайдер с запасным источником
    def __init__(self, primary, fallback):  # Конструктор принимает основной и запасной провайдеры
        if not isinstance(primary, ExchangeRateProvider) or not isinstance(fallback, ExchangeRateProvider):  # Проверяем типы обоих источников
            raise DomainError("INVALID_CONFIG")  # Ошибка, если хотя бы один не является провайдером
        self.primary = primary  # Сохраняем основной источник
        self.fallback = fallback  # Сохраняем запасной источник

    def get_rate(self, source, target):  # Реализация метода получения курса
        try:  # Блок для запроса к основному источнику
            rate = self.primary.get_rate(source, target)  # Пытаемся получить курс у основного источника
        except DomainError as e:  # Перехватываем ошибки основного источника
            if e.code == "RATE_NOT_FOUND":  # Если основной источник не нашел курс
                rate = self.fallback.get_rate(source, target)  # Запрашиваем курс у запасного
            else:  # Если произошла другая ошибка
                raise e  # Пробрасываем её наружу

        if not isinstance(rate, ExchangeRate) or not rate.matches(source, target):  # Проверяем корректность итогового курса
            raise DomainError("INVALID_RATE_PAIR")  # Ошибка, если курс не того типа или направления
        return rate  # Возвращаем корректный курс
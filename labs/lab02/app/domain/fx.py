from dataclasses import dataclass  # Инструмент для классов данных
from decimal import Decimal  # Тип для точных вычислений
from app.support.types import currency, decimal_value  # Валидаторы
from app.support.errors import DomainError  # Ошибки 


@dataclass(frozen=True)  # Класс данных + неизменяемость
class ExchangeRate:  # Модель курса валют
    source: str  # Исходная валюта 
    target: str  # Целевая валюта 
    rate: Decimal  # Значение курса 
    
    def __post_init__(self):  # Проверки после создания объекта
        currency(self.source)  # Проверяем исходную валюту
        currency(self.target)  # Проверяем целевую валюту
        decimal_value(self.rate, "INVALID_RATE")  # Проверяем тип курса

        
        if not self.rate.is_finite() or self.rate <= 0: # Курс должен быть конечным и строго положительным
            raise DomainError("INVALID_RATE")  

        
        if self.source == self.target: # Валюты в паре не должны совпадать
            raise DomainError("INVALID_RATE_PAIR")  
        
    def matches(self, source, target):  # Проверка соответствия паре
        return self.source == source and self.target == target  # Сравнение
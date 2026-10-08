from dataclasses import dataclass 
from decimal import Decimal
from app.support.errors import DomainError 
from app.support.types import currency, decimal_value

@dataclass(frozen=True) # после создания объект нельзя изменить
class ExchangeRate: 
    source: str # что
    target: str # куда
    rate: Decimal # курс

def __post_init__(self): # проверка объекта
    currency(self.source) # валюта написана верно
    currency(self.target)

    if self.source == self.target: # одинаковые валюты
        raise DomainError("INVALID_RATE_PAIR")

    decimal_value(self.rate, "INVALID_RATE") # курс — это Decimal, не float

    if self.rate <= 0:
        raise DomainError("INVALID_RATE") # курс больше нуля

def describe(self):
    return f"{self.source}/{self.target}={self.rate}"
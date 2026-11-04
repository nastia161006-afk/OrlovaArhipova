from dataclasses import dataclass 
from decimal import Decimal
from app.support.errors import DomainError 
from app.support.types import currency, decimal_value
@dataclass(frozen=True) 
class ExchangeRate: 
    source: str 
    target: str 
    rate: Decimal

def __post_init__(self):
    currency(self.source)
    currency(self.target)

    if self.source == self.target:
        raise DomainError("INVALID_RATE_PAIR")

    decimal_value(self.rate, "INVALID_RATE")

    if self.rate <= 0:
        raise DomainError("INVALID_RATE")

def describe(self):
    return f"{self.source}/{self.target}={self.rate}"
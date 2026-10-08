from dataclasses import dataclass
from decimal import Decimal
from app.support.types import currency, decimal_value
from app.support.errors import DomainError


@dataclass(frozen=True)
class ExchangeRate:
    source: str
    target: str
    rate: Decimal

    def __post_init__(self):
        currency(self.source)
        currency(self.target)
        decimal_value(self.rate, "INVALID_RATE")

        if not self.rate.is_finite() or self.rate <= 0:
            raise DomainError("INVALID_RATE")

        if self.source == self.target:
            raise DomainError("INVALID_RATE_PAIR")

    def matches(self, source, target):
        return self.source == source and self.target == target
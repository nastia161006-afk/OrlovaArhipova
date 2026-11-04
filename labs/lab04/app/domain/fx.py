from dataclasses import dataclass
from decimal import Decimal
from app.support.types import currency, decimal_value
from app.support.errors import DomainError

frozen=True
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

        def matches(self, source, target):
        return legacy_l4_exchangerate_matches(self, source, target)

def legacy_l4_exchangerate_matches(owner, source, target):
    return owner.source == source and owner.target == target
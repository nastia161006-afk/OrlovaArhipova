from decimal import localcontext
from app.support.types import currency, rounded_money
from app.support.errors import DomainError


def make_entity(source, target, rate):
    return dict(source=source,target=target,rate=rate)


def _new_legacy_service(rates):
    return {"rates": dict(rates)}


def view(rate):
    return dict(rate)


def invoke(service,method,amount,target_currency):
    if method != "convert":raise ValueError(method)
    currency(target_currency)
    if amount.currency==target_currency:return amount
    pair=(amount.currency,target_currency)
    if pair not in service["rates"]:raise DomainError("RATE_NOT_FOUND")
    with localcontext() as ctx:
        ctx.prec=28
        return rounded_money(amount.amount*service["rates"][pair]["rate"],target_currency)


from decimal import Decimal

def new_service(rates=None):
    return _new_legacy_service({("USD","EUR"):make_entity("USD","EUR",Decimal("0.85"))} if rates is None else rates)

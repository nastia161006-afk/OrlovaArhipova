from decimal import Decimal
from app.services.fx_service import FxService, make_entity
from app.domain.providers import TableRateProvider

def build_service(provider=None, rates=None):
    if rates is None:
        rates = {("USD","EUR"): make_entity("USD","EUR",Decimal("0.85"))}
        
    if provider is None:
        provider = TableRateProvider(rates)
        
    return FxService(provider)
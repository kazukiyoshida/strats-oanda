from typing import Optional

from strats.model import PricesData

from ..model import ClientPrice


def client_price_to_prices(p: ClientPrice) -> Optional[PricesData]:
    if len(p.bids) == 0 or len(p.asks) == 0:
        return None
    return PricesData(
        bid=p.bids[0].price,
        ask=p.asks[0].price,
    )

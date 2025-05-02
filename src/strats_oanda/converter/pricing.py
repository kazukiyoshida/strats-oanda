from strats.model import PricesData

from ..model import ClientPrice


def client_price_to_prices_data(p: ClientPrice, _current_data: PricesData) -> PricesData:
    if len(p.bids) == 0 or len(p.asks) == 0:
        raise ValueError("bids and asks must be not empty")
    return PricesData(
        bid=p.bids[0].price,
        ask=p.asks[0].price,
    )

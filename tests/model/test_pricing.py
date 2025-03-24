from datetime import datetime, timezone
from decimal import Decimal

from strats_oanda.model.pricing import ClientPrice, PriceBucket, parse_client_price


def test_parse_client_price():
    data = {
        "type": "PRICE",
        "time": "2025-03-24T15:34:25.366624289Z",
        "bids": [
            {"price": "150.693", "liquidity": 250000},
        ],
        "asks": [
            {"price": "150.697", "liquidity": 250000},
        ],
        "closeoutBid": "150.687",
        "closeoutAsk": "150.703",
        "status": "tradeable",
        "tradeable": True,
        "instrument": "USD_JPY",
    }
    expect = ClientPrice(
        type="PRICE",
        instrument="USD_JPY",
        time=datetime(2025, 3, 24, 15, 34, 25, 366624, tzinfo=timezone.utc),
        tradeable=True,
        bids=[
            PriceBucket(
                price=Decimal("150.693"),
                liquidity=250000,
            ),
        ],
        asks=[
            PriceBucket(
                price=Decimal("150.697"),
                liquidity=250000,
            ),
        ],
        closeout_bid=Decimal("150.687"),
        closeout_ask=Decimal("150.703"),
    )
    assert parse_client_price(data) == expect

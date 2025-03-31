from datetime import datetime, timezone
from decimal import Decimal

from strats_oanda.model import ClientPrice, PriceBucket, parse_client_price


def test_parse_client_price():
    data = {
        "type": "PRICE",
        "timestamp": "2025-03-24T15:34:25.366624289Z",
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
        time=None,
        timestamp=datetime(2025, 3, 24, 15, 34, 25, 366624, tzinfo=timezone.utc),
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


def test_parse_client_price_in_pricing_stream_api():
    data = {
        "type": "PRICE",
        "time": "2025-03-31T15:31:22.518120299Z",
        "bids": [
            {"price": "149.732", "liquidity": 250000},
        ],
        "asks": [
            {"price": "149.736", "liquidity": 250000},
        ],
        "closeoutBid": "149.727",
        "closeoutAsk": "149.742",
        "status": "tradeable",
        "tradeable": True,
        "instrument": "USD_JPY",
    }
    expect = ClientPrice(
        type="PRICE",
        instrument="USD_JPY",
        time=datetime(2025, 3, 31, 15, 31, 22, 518120, tzinfo=timezone.utc),
        timestamp=None,
        tradeable=True,
        bids=[
            PriceBucket(
                price=Decimal("149.732"),
                liquidity=250000,
            ),
        ],
        asks=[
            PriceBucket(
                price=Decimal("149.736"),
                liquidity=250000,
            ),
        ],
        closeout_bid=Decimal("149.727"),
        closeout_ask=Decimal("149.742"),
    )
    assert parse_client_price(data) == expect

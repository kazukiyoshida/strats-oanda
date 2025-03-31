from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from ..helper import parse_time


# https://developer.oanda.com/rest-live-v20/pricing-common-df/#PriceBucket
@dataclass
class PriceBucket:
    price: Decimal
    liquidity: int


def parse_price_bucket(data: dict) -> PriceBucket:
    return PriceBucket(
        price=Decimal(data["price"]),
        liquidity=data["liquidity"],
    )


# https://developer.oanda.com/rest-live-v20/pricing-df/#ClientPrice
@dataclass
class ClientPrice:
    type: str
    instrument: Optional[str]
    # BUG: pricing stream API では time が返されるが、
    # transaction stream API の子要素では timestamp が返される.
    time: Optional[datetime]
    timestamp: Optional[datetime]
    tradeable: Optional[bool]
    bids: list[PriceBucket]
    asks: list[PriceBucket]
    closeout_bid: Decimal
    closeout_ask: Decimal


def parse_client_price(data: dict) -> ClientPrice:
    return ClientPrice(
        type=data["type"] if "type" in data else "PRICE",
        instrument=data["instrument"] if "instrument" in data else None,
        time=parse_time(data["time"]) if "time" in data else None,
        timestamp=parse_time(data["timestamp"]) if "timestamp" in data else None,
        tradeable=data["tradeable"] if "tradeable" in data else None,
        bids=[parse_price_bucket(x) for x in data["bids"]],
        asks=[parse_price_bucket(x) for x in data["asks"]],
        closeout_bid=Decimal(data["closeoutBid"]),
        closeout_ask=Decimal(data["closeoutAsk"]),
    )


# https://developer.oanda.com/rest-live-v20/pricing-df/#PricingHeartbeat
@dataclass
class PricingHeartbeat:
    type: str
    time: datetime

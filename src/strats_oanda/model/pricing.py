from datetime import datetime
from dataclasses import dataclass
from decimal import Decimal

from .common import parse_time


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
    instrument: str
    time: datetime
    tradeable: bool
    bids: list[PriceBucket]
    asks: list[PriceBucket]
    closeout_bid: Decimal
    closeout_ask: Decimal


def parse_client_price(data: dict) -> ClientPrice:
    return ClientPrice(
        type=data["type"],
        instrument=data["instrument"],
        time=parse_time(data["time"]),
        tradeable=data["tradeable"],
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

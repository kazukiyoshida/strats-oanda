from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from ..helper import parse_time


# https://developer.oanda.com/rest-live-v20/instrument-df/#CandlestickGranularity
class CandlestickGranularity(Enum):
    M1 = "M1"  # 1 minute candlesticks, minute alignment
    # ...


# https://developer.oanda.com/rest-live-v20/instrument-df/#CandlestickData
@dataclass
class CandlestickData:
    o: Decimal
    h: Decimal
    l: Decimal
    c: Decimal


def parse_candlestick_data(data: dict) -> CandlestickData:
    return CandlestickData(
        o=Decimal(data["o"]),
        h=Decimal(data["h"]),
        l=Decimal(data["l"]),
        c=Decimal(data["c"]),
    )


# https://developer.oanda.com/rest-live-v20/instrument-df/#Candlestick
@dataclass
class Candlestick:
    time: datetime
    volume: int
    complete: bool
    bid: Optional[CandlestickData] = None
    ask: Optional[CandlestickData] = None
    mid: Optional[CandlestickData] = None


def parse_candlestick(data: dict) -> Candlestick:
    return Candlestick(
        time=parse_time(data["time"]),
        volume=data["volume"],
        complete=data["complete"],
        bid=parse_candlestick_data(data["bid"]) if "bid" in data else None,
        ask=parse_candlestick_data(data["ask"]) if "ask" in data else None,
        mid=parse_candlestick_data(data["mid"]) if "mid" in data else None,
    )

# Instrument Endpoint
# cf. https://developer.oanda.com/rest-live-v20/instrument-ep/
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import requests

from strats_oanda.config import get_config
from strats_oanda.helper import format_datetime
from strats_oanda.logger import logger
from strats_oanda.model.instrument import (
    Candlestick,
    CandlestickGranularity,
    parse_candlestick,
)


@dataclass
class GetCandlesQueryParams:
    count: Optional[int] = None
    from_time: Optional[datetime] = None
    to_time: Optional[datetime] = None


@dataclass
class GetCandlesResponse:
    instrument: str
    granularity: CandlestickGranularity
    candles: list[Candlestick]


def parse_get_candles_response(data) -> GetCandlesResponse:
    return GetCandlesResponse(
        instrument=data["instrument"],
        granularity=CandlestickGranularity(data["granularity"]),
        candles=[parse_candlestick(x) for x in data["candles"]],
    )


class InstrumentClient:
    def __init__(self):
        self.config = get_config()

    def get_candles(
        self,
        instrument: str,
        params: GetCandlesQueryParams,
    ) -> Optional[GetCandlesResponse]:
        url = f"{self.config.rest_url}/v3/instruments/{instrument}/candles"
        payload = {
            # PricingComponent
            # Can contain any combination of the characters “M” (midpoint candles)
            # “B” (bid candles) and “A” (ask candles).
            # cf. https://developer.oanda.com/rest-live-v20/primitives-df/#PricingComponent
            "price": "M",
            "granularity": "M1",
        }
        if params.count is not None:
            payload["count"] = str(params.count)
        if params.from_time is not None:
            payload["from"] = format_datetime(params.from_time)
        if params.to_time is not None:
            payload["to"] = format_datetime(params.to_time)

        headers = {
            "Authorization": f"Bearer {self.config.token}",
            "Content-Type": "application/json",
        }
        res = requests.get(url, headers=headers, params=payload)

        if res.status_code == 200:
            return parse_get_candles_response(res.json())
        logger.error(f"Error get candles data: {res.status_code} {res.text}")
        return None

# Instrument Endpoint
# cf. https://developer.oanda.com/rest-live-v20/instrument-ep/
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import aiohttp

from strats_oanda.config import get_config
from strats_oanda.helper import format_datetime
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

    async def get_candles(
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
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=payload) as res:
                if res.status == 200:
                    obj = await res.json()
                    return parse_get_candles_response(obj)
                else:
                    text = await res.text()
                    raise RuntimeError(
                        f"failed to create a session: status={res.status}, text={text}"
                    )

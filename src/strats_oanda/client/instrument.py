# Instrument Endpoint
# cf. https://developer.oanda.com/rest-live-v20/instrument-ep/
from dataclasses import dataclass
from datetime import datetime
import requests

from strats_oanda.logger import logger
from strats_oanda.client.common import format_datetime_for_oanda
from strats_oanda.model.instrument import CandlestickGranularity, Candlestick, parse_candlestick


@ dataclass
class GetCandlesQueryParams:
    count: int | None = None
    from_time: datetime | None = None
    to_time: datetime | None = None


@ dataclass
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
    def __init__(self, url, token):
        self.url = url
        self.token = token

    def get_candles(self, instrument: str, params: GetCandlesQueryParams) -> GetCandlesResponse | None:
        url = f"{self.url}/v3/instruments/{instrument}/candles"
        payload = {
            # PricingComponent
            # Can contain any combination of the characters “M” (midpoint candles)
            # “B” (bid candles) and “A” (ask candles).
            # cf. https://developer.oanda.com/rest-live-v20/primitives-df/#PricingComponent
            "price": "M",
            "granularity": "M1",
        }
        if params.count is not None:
            payload["count"] = params.count
        if params.from_time is not None:
            payload["from"] = format_datetime_for_oanda(params.from_time)
        if params.to_time is not None:
            payload["to"] = format_datetime_for_oanda(params.to_time)

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        res = requests.get(url, headers=headers, params=payload)

        if res.status_code == 200:
            return parse_get_candles_response(res.json())
        else:
            logger.error(f"Error get candles data: {res.status_code} {res.text}")
            return None

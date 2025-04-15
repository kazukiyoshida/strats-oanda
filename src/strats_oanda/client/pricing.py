"""
Pricing Stream Endpoints
cf. https://developer.oanda.com/rest-live-v20/pricing-ep/
"""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator

import aiohttp
from strats.exchange import StreamClient

from strats_oanda.config import get_config
from strats_oanda.model.pricing import ClientPrice, parse_client_price

logger = logging.getLogger(__name__)


class PricingStreamClient(StreamClient):
    def __init__(self, instruments: list[str]):
        if not isinstance(instruments, list):
            raise ValueError(f"instruments must be list: {instruments}")
        self.config = get_config()
        self.instruments = instruments

    async def stream(self) -> AsyncGenerator[ClientPrice]:
        try:
            logger.info("PricingStreamClient start")

            url = f"{self.config.account_streaming_url}/pricing/stream"
            params = {"instruments": ",".join(self.instruments)}
            headers = {
                "Authorization": f"Bearer {self.config.token}",
                "Accept-Datetime-Format": "RFC3339",
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as resp:
                    if resp.status != 200:
                        raise RuntimeError(f"failed to connect: status={resp.status}")

                    async for line_bytes in resp.content:
                        line = line_bytes.decode("utf-8")

                        if not line or "HEARTBEAT" in line:
                            continue

                        try:
                            msg = json.loads(line)
                            yield parse_client_price(msg)
                        except Exception as e:
                            logger.error(f"failed to parse message: {e}, {line=}")
                            continue

        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"Unhandled exception in PricingStreamClient: {e}")
        finally:
            logger.info("PricingStreamClient stopped")

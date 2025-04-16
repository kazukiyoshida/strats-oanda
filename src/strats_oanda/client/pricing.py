"""
Pricing Stream Endpoints
cf. https://developer.oanda.com/rest-live-v20/pricing-ep/
"""

import asyncio
import json
import logging
import random
from collections.abc import AsyncGenerator

import aiohttp
from aiohttp import ClientConnectionError, ClientPayloadError, ServerDisconnectedError
from strats.exchange import StreamClient

from strats_oanda.config import get_config
from strats_oanda.model.pricing import ClientPrice, parse_client_price

logger = logging.getLogger(__name__)


class PricingStreamClient(StreamClient):
    MAX_RETRIES = 5
    BASE_DELAY = 1.0  # seconds

    def __init__(self, instruments: list[str]):
        if not isinstance(instruments, list):
            raise ValueError(f"instruments must be list: {instruments}")
        self.config = get_config()
        self.instruments = instruments

    def set_name(self, name: str):
        self.name = name

    async def stream(self) -> AsyncGenerator[ClientPrice, None]:
        attempt = 0

        while True:
            try:
                logger.info(f"{self.name} Connecting...")

                url = f"{self.config.account_streaming_url}/pricing/stream"
                params = {"instruments": ",".join(self.instruments)}
                headers = {
                    "Authorization": f"Bearer {self.config.token}",
                    "Accept-Datetime-Format": "RFC3339",
                }

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, params=params) as resp:
                        if resp.status != 200:
                            raise RuntimeError(f"Failed to connect: status={resp.status}")

                        logger.info("{self.name} Connected to OANDA pricing stream")
                        attempt = 0  # reset retry count on success

                        async for line_bytes in resp.content:
                            line = line_bytes.decode("utf-8").strip()

                            if not line or "HEARTBEAT" in line:
                                continue

                            try:
                                msg = json.loads(line)
                                yield parse_client_price(msg)
                            except Exception as e:
                                logger.error(f"{self.name} Failed to parse message: {e}, {line=}")
                                continue

            except asyncio.CancelledError:
                logger.info(f"{self.name} cancelled")
                raise

            except (
                ClientConnectionError,
                ClientPayloadError,
                ServerDisconnectedError,
                asyncio.TimeoutError,
            ) as e:
                logger.warning(
                    f"{self.name} Stream disconnected (retryable): {type(e).__name__}: {e}"
                )

            except Exception as e:
                logger.error(
                    f"{self.name} Unhandled exception in PricingStreamClient:"
                    f"{type(e).__name__}: {e}"
                )

            finally:
                logger.info(f"{self.name} Disconnected from pricing stream")

            attempt += 1
            if attempt > self.MAX_RETRIES:
                logger.error(
                    f"{self.name} Max retry attempts exceeded({self.MAX_RETRIES}), giving up."
                )
                break

            delay = self.BASE_DELAY * (2 ** (attempt - 1)) + random.uniform(0, 1)
            logger.info(f"{self.name} Retrying in {delay:.1f} seconds... (attempt {attempt})")
            await asyncio.sleep(delay)

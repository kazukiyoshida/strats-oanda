"""
Pricing Stream Endpoints
cf. https://developer.oanda.com/rest-live-v20/pricing-ep/
"""

import asyncio
import json
import logging
import random
from collections.abc import AsyncGenerator
from typing import Optional

import aiohttp
from aiohttp import ClientConnectionError, ClientPayloadError, ServerDisconnectedError
from strats.monitor import StreamClient

from strats_oanda.config import get_config
from strats_oanda.model.pricing import ClientPrice, parse_client_price

logger = logging.getLogger(__name__)


class PricingStreamClient(StreamClient):
    _counter = 0

    def __init__(
        self,
        instruments: list[str],
        name: Optional[str] = None,
        max_retries: int = 5,
        base_delay: float = 1.0,  # seconds
    ):
        if not isinstance(instruments, list):
            raise ValueError(f"instruments must be list: {instruments}")

        # Update class-specific counter
        type(self)._counter += 1

        self.name = name or f"{type(self).__name__}_{type(self)._counter}"
        self.config = get_config()
        self.instruments = instruments
        self.max_retries = max_retries
        self.base_delay = base_delay

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
                timeout = aiohttp.ClientTimeout(total=60 * 60 * 24)

                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(url, headers=headers, params=params) as resp:
                        if resp.status != 200:
                            raise RuntimeError(f"Failed to connect: status={resp.status}")

                        logger.info(f"{self.name} Connected to OANDA pricing stream")
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
            if attempt > self.max_retries:
                logger.error(
                    f"{self.name} Max retry attempts exceeded({self.max_retries}), giving up."
                )
                break

            delay = self.base_delay * (2 ** (attempt - 1)) + random.uniform(0, 1)
            logger.info(f"{self.name} Retrying in {delay:.1f} seconds... (attempt {attempt})")
            await asyncio.sleep(delay)

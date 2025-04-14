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

    async def stream(self, stop_event: asyncio.Event) -> AsyncGenerator[ClientPrice]:
        logger.info("start OANDA /pricing/stream API")

        url = f"{self.config.account_streaming_url}/pricing/stream"
        params = {"instruments": ",".join(self.instruments)}
        headers = {
            "Authorization": f"Bearer {self.config.token}",
            "Accept-Datetime-Format": "RFC3339",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as resp:
                content_iter = resp.content.__aiter__()

                while not stop_event.is_set():
                    next_line_task = asyncio.create_task(
                        content_iter.__anext__(),
                        name="pricing-stream-client-next-line-task",
                    )
                    stop_task = asyncio.create_task(
                        stop_event.wait(),
                        name="pricing-stream-client-stop-task",
                    )

                    done, pending = await asyncio.wait(
                        [next_line_task, stop_task],
                        return_when=asyncio.FIRST_COMPLETED,
                    )

                    for task in pending:
                        task.cancel()
                        # In order to handle the following error msg,
                        # await task and catch an exception
                        # > Task exception was never retrieved
                        # > aiohttp.client_exceptions.ClientConnectionError: Connection closed
                        try:
                            await task
                        except Exception as e:
                            logger.error(f"cancelled task raised: {e}")

                    if stop_task in done:
                        logger.info("OANDA /pricing/stream API stopped")
                        break

                    if next_line_task in done:
                        try:
                            line_bytes = next_line_task.result()
                        except (StopAsyncIteration, asyncio.CancelledError) as e:
                            logger.error(f"async iteration stopped or canceled. {e}")
                            break

                        line = line_bytes.decode("utf-8").strip()
                        if not line or "HEARTBEAT" in line:
                            continue

                        try:
                            data = json.loads(line)
                            yield parse_client_price(data)
                        except Exception as e:
                            logger.error(f"failed to parse message. err={e}, line={line}")
                            continue

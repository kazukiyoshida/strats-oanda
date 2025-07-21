"""
Transaction Stream Endpoints
cf. https://developer.oanda.com/rest-live-v20/transaction-ep/
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
from strats_oanda.model.transaction import (
    Transaction,
    parse_limit_order_transaction,
    parse_order_cancel_transaction,
    parse_order_fill_transaction,
)

logger = logging.getLogger(__name__)


class TransactionClient(StreamClient):
    _counter = 0

    def __init__(
        self,
        name: Optional[str] = None,
        max_retries: int = 5,
        base_delay: float = 1.0,  # seconds
    ):
        # Update class-specific counter
        type(self)._counter += 1

        self.name = name or f"{type(self).__name__}_{type(self)._counter}"
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.config = get_config()

    async def stream(self) -> AsyncGenerator[Transaction, None]:
        attempt = 0

        while True:
            try:
                logger.info(f"{self.name} connecting...")

                url = f"{self.config.account_streaming_url}/transactions/stream"
                headers = {
                    "Authorization": f"Bearer {self.config.token}",
                }
                timeout = aiohttp.ClientTimeout(total=60 * 60 * 24)

                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(url, headers=headers) as resp:
                        if resp.status != 200:
                            raise RuntimeError(f"Failed to connect: status={resp.status}")

                        logger.info(f"{self.name} Connected to OANDA transaction stream")
                        attempt = 0  # reset on success

                        async for line_bytes in resp.content:
                            line = line_bytes.decode("utf-8").strip()

                            if not line or "HEARTBEAT" in line:
                                continue

                            try:
                                data = json.loads(line)
                                tx_type = data.get("type")

                                tx: Optional[Transaction] = None
                                if tx_type == "LIMIT_ORDER":
                                    tx = parse_limit_order_transaction(data)
                                elif tx_type == "ORDER_CANCEL":
                                    tx = parse_order_cancel_transaction(data)
                                elif tx_type == "ORDER_FILL":
                                    tx = parse_order_fill_transaction(data)
                                elif tx_type == "HEARTBEAT":
                                    continue
                                else:
                                    logger.warning(
                                        f"{self.name} Unknown transaction type received: {data}"
                                    )
                                    continue

                                if tx is not None:
                                    yield tx
                            except Exception as e:
                                logger.error(
                                    f"{self.name} Failed to parse transaction message: {e}, {line=}"
                                )
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
                    f"{self.name} Stream disconnected (retryable):{type(e).__name__}: {e}"
                )

            except Exception as e:
                logger.error(
                    f"{self.name} Unhandled exception in TransactionClient:{type(e).__name__}: {e}"
                )

            finally:
                logger.info(f"{self.name} Disconnected from transaction stream")

            attempt += 1
            if attempt > self.max_retries:
                logger.error(
                    f"{self.name} Max retry attempts exceeded({self.max_retries}), giving up."
                )
                break

            delay = self.base_delay * (2 ** (attempt - 1)) + random.uniform(0, 1)
            logger.info(f"{self.name} Retrying in {delay:.1f} seconds... (attempt {attempt})")
            await asyncio.sleep(delay)

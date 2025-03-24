"""
Transaction Stream Endpoints
cf. https://developer.oanda.com/rest-live-v20/transaction-ep/
"""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator
from typing import Optional

import aiohttp
from strats.exchange import StreamClient

from strats_oanda.config import get_config
from strats_oanda.model.transaction import (
    Transaction,
    parse_limit_order_transaction,
    parse_order_cancel_transaction,
    parse_order_fill_transaction,
)

logger = logging.getLogger(__name__)


class TransactionClient(StreamClient):
    def __init__(self):
        self.config = get_config()

    async def stream(self, stop_event: asyncio.Event) -> AsyncGenerator[Transaction]:
        url = f"{self.config.account_streaming_url}/transactions/stream"
        headers = {
            "Authorization": f"Bearer {self.config.token}",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                content_iter = resp.content.__aiter__()

                while not stop_event.is_set():
                    next_line_task = asyncio.create_task(content_iter.__anext__())
                    stop_task = asyncio.create_task(stop_event.wait())

                    done, pending = await asyncio.wait(
                        [next_line_task, stop_task],
                        return_when=asyncio.FIRST_COMPLETED,
                    )

                    # 不必要になった一時的な task は終了
                    for task in pending:
                        task.cancel()

                    if stop_task in done:
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
                                logger.warn(f"unknown transaction arrived. {data}")
                                continue

                            if tx is not None:
                                yield tx

                        except Exception as e:
                            logger.error(f"failed to parse message. err={e}, line={line}")
                            continue

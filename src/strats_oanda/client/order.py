"""
Order Endpoints Client
cf. https://developer.oanda.com/rest-live-v20/order-ep/
"""

import asyncio
import json
import logging
from dataclasses import asdict
from typing import Optional

import aiohttp

from strats_oanda.config import get_config
from strats_oanda.helper import JSONEncoder, remove_none, to_camel_case
from strats_oanda.model import (
    CancelOrderResponse,
    CreateLimitOrderResponse,
    CreateMarketOrderResponse,
    LimitOrderRequest,
    MarketOrderRequest,
    parse_cancel_order_response,
    parse_create_limit_order_response,
    parse_create_market_order_response,
)

logger = logging.getLogger(__name__)


class OrderClient:
    def __init__(self, keepalive_timeout: float = 60.0, max_retries: int = 2):
        self.config = get_config()
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.token}",
        }
        self.keepalive_timeout = keepalive_timeout
        self.max_retries = max_retries
        self.session: Optional[aiohttp.ClientSession] = None
        self._owns_session = False

    async def open(self):
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(keepalive_timeout=self.keepalive_timeout)
            self.session = aiohttp.ClientSession(headers=self.headers, connector=connector)
            self._owns_session = True

    async def close(self):
        if self._owns_session and self.session and not self.session.closed:
            await self.session.close()

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _request_with_retry(
        self, method: str, url: str, **kwargs
    ) -> Optional[aiohttp.ClientResponse]:
        if self.session is None or self.session.closed:
            raise RuntimeError("ClientSession is not open. Call 'await open()' first.")

        for attempt in range(1, self.max_retries + 2):
            try:
                async with self.session.request(method, url, **kwargs) as res:
                    return res
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.warning(f"Request {method} {url} failed (attempt {attempt}): {e}")
                if attempt < self.max_retries + 1:
                    await asyncio.sleep(1)
                else:
                    logger.error("All retry attempts failed.")
                    return None
        return None  # ここには到達しない

    async def create_market_order(
        self,
        market_order: MarketOrderRequest,
    ) -> Optional[CreateMarketOrderResponse]:
        url = f"{self.config.account_rest_url}/orders"
        req = to_camel_case(remove_none({"order": asdict(market_order)}))
        order_data = json.dumps(req, cls=JSONEncoder)
        logger.info(f"create market order: {order_data}")

        res = await self._request_with_retry("POST", url, data=order_data)
        if res is None:
            return None

        if res.status == 201:
            data = await res.json()
            logger.info("create market order success")
            try:
                return parse_create_market_order_response(data)
            except Exception as e:
                logger.exception(f"Failed to parse market order response: {e}")
                return None
        else:
            text = await res.text()
            logger.error(f"error creating market order: {res.status} {text}")
            return None

    async def create_limit_order(
        self,
        limit_order: LimitOrderRequest,
    ) -> Optional[CreateLimitOrderResponse]:
        url = f"{self.config.account_rest_url}/orders"
        req = to_camel_case(remove_none({"order": asdict(limit_order)}))
        order_data = json.dumps(req, cls=JSONEncoder)
        logger.info(f"create limit order: {order_data}")

        res = await self._request_with_retry("POST", url, data=order_data)
        if res is None:
            return None

        if res.status == 201:
            data = await res.json()
            logger.info("create limit order success")
            return parse_create_limit_order_response(data)
        else:
            text = await res.text()
            logger.error(f"error creating limit order: {res.status} {text}")
            return None

    async def cancel_limit_order(self, order_id: str) -> Optional[CancelOrderResponse]:
        url = f"{self.config.account_rest_url}/orders/{order_id}/cancel"
        logger.info(f"cancel order: {order_id=}")

        res = await self._request_with_retry("PUT", url)
        if res is None:
            return None

        if res.status == 200:
            data = await res.json()
            logger.info(f"cancel limit order success: {data}")
            return parse_cancel_order_response(data)
        else:
            text = await res.text()
            logger.error(f"error canceling order: {res.status} {text}")
            return None

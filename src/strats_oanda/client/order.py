"""
Order Endpoints Client
cf. https://developer.oanda.com/rest-live-v20/order-ep/
"""

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

    async def open(self):
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            connector=aiohttp.TCPConnector(
                keepalive_timeout=self.keepalive_timeout,
            ),
        )

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
        else:
            raise ValueError("session is not opened")

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def create_market_order(
        self,
        market_order: MarketOrderRequest,
    ) -> CreateMarketOrderResponse:
        url = f"{self.config.account_rest_url}/orders"
        req = to_camel_case(remove_none({"order": asdict(market_order)}))
        order_data = json.dumps(req, cls=JSONEncoder)
        logger.info(f"create market order: {order_data}")

        data = await self._request("POST", url, data=order_data)
        logger.info("create market order success")
        return parse_create_market_order_response(data)

    async def create_limit_order(
        self,
        limit_order: LimitOrderRequest,
    ) -> CreateLimitOrderResponse:
        url = f"{self.config.account_rest_url}/orders"
        req = to_camel_case(remove_none({"order": asdict(limit_order)}))
        order_data = json.dumps(req, cls=JSONEncoder)
        logger.info(f"create limit order: {order_data}")

        data = await self._request("POST", url, data=order_data)
        logger.info("create limit order success")
        return parse_create_limit_order_response(data)

    async def cancel_limit_order(self, order_id: str) -> CancelOrderResponse:
        url = f"{self.config.account_rest_url}/orders/{order_id}/cancel"
        logger.info(f"cancel order: {order_id=}")

        data = await self._request("PUT", url)
        logger.info(f"cancel limit order success: {data}")
        return parse_cancel_order_response(data)

    async def _request(self, method: str, url: str, **kwargs) -> dict:
        if self.session is None or self.session.closed:
            raise RuntimeError(
                "ClientSession is not open. Use `async with OrderClient() as client:` format",
            )

        async with self.session.request(method, url, **kwargs) as res:
            if res.status == 201 or res.status == 200:
                return await res.json()
            else:
                text = await res.text()
                raise RuntimeError(f"error order request: http_status={res.status} text={text}")

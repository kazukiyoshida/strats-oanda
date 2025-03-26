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
from strats_oanda.helper import JSONEncoder, remove_none
from strats_oanda.model import (
    CancelOrderResponse,
    CreateLimitOrderResponse,
    LimitOrderRequest,
    parse_cancel_order_response,
    parse_create_limit_order_response,
)

logger = logging.getLogger(__name__)


class OrderClient:
    def __init__(self):
        self.config = get_config()
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.token}",
        }

    async def create_limit_order(
        self,
        limit_order: LimitOrderRequest,
    ) -> Optional[CreateLimitOrderResponse]:
        url = f"{self.config.account_rest_url}/orders"
        req = remove_none({"order": asdict(limit_order)})
        order_data = json.dumps(req, cls=JSONEncoder)

        logger.info(f"create limit order: {order_data}")

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(url, data=order_data) as res:
                if res.status == 201:
                    data = await res.json()
                    logger.info(f"create limit order success: {data}")
                    return parse_create_limit_order_response(data)
                else:
                    text = await res.text()
                    logger.error(f"Error creating order: {res.status} {text}")
                    return None

    async def cancel_limit_order(self, order_id: str) -> Optional[CancelOrderResponse]:
        url = f"{self.config.account_rest_url}/orders/{order_id}/cancel"

        logger.info(f"cancel order: {order_id=}")

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.put(url) as res:
                if res.status == 200:
                    data = await res.json()
                    logger.info(f"cancel limit order success: {data}")
                    return parse_cancel_order_response(data)
                else:
                    text = await res.text()
                    logger.error(f"Error canceling order: {res.status} {text}")
                    return None

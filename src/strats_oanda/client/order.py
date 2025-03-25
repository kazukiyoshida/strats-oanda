"""
Order Endpoints Client
cf. https://developer.oanda.com/rest-live-v20/order-ep/
"""

import json
import logging
from dataclasses import asdict, dataclass
from typing import Optional

import aiohttp

from strats_oanda.helper import JSONEncoder, remove_none
from strats_oanda.model.order import LimitOrderRequest
from strats_oanda.model.transaction import (
    LimitOrderTransaction,
    OrderCancelTransaction,
    parse_limit_order_transaction,
    parse_order_cancel_transaction,
)

logger = logging.getLogger(__name__)


@dataclass
class CreateLimitOrderResponse:
    orderCreateTransaction: LimitOrderTransaction
    relatedTransactionIDs: list[str]
    lastTransactionID: str


def parse_create_limit_order_response(data: dict) -> CreateLimitOrderResponse:
    return CreateLimitOrderResponse(
        orderCreateTransaction=parse_limit_order_transaction(data["orderCreateTransaction"]),
        relatedTransactionIDs=data["relatedTransactionIDs"],
        lastTransactionID=data["lastTransactionID"],
    )


@dataclass
class CancelOrderResponse:
    orderCancelTransaction: OrderCancelTransaction
    relatedTransactionIDs: list[str]
    lastTransactionID: str


def parse_cancel_order_response(data: dict) -> CancelOrderResponse:
    return CancelOrderResponse(
        orderCancelTransaction=parse_order_cancel_transaction(data["orderCancelTransaction"]),
        relatedTransactionIDs=data["relatedTransactionIDs"],
        lastTransactionID=data["lastTransactionID"],
    )


class OrderClient:
    def __init__(self, url: str, account: str, token: str):
        self.url = url
        self.account = account
        self.token = token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

    async def create_limit_order(
        self,
        limit_order: LimitOrderRequest,
    ) -> Optional[CreateLimitOrderResponse]:
        url = f"{self.url}/v3/accounts/{self.account}/orders"
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
        url = f"{self.url}/v3/accounts/{self.account}/orders/{order_id}/cancel"

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

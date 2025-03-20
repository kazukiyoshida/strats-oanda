# Order Endpoints Client
# cf. https://developer.oanda.com/rest-live-v20/order-ep/
import requests
import json
from dataclasses import dataclass
from dataclasses import asdict

from strats_oanda.logger import logger
from strats_oanda.model.order import LimitOrderRequest
from strats_oanda.model.transaction import \
    LimitOrderTransaction, parse_limit_order_transaction, \
    OrderCancelTransaction, parse_order_cancel_transaction
from strategy_server.utils.json import JSONEncoder, remove_none


@ dataclass
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


@ dataclass
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
    def __init__(self, url, account, token):
        self.url = url
        self.account = account
        self.token = token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    def create_limit_order(self, limit_order: LimitOrderRequest) -> CreateLimitOrderResponse | None:
        url = f"{self.url}/v3/accounts/{self.account}/orders"
        req = remove_none({
            "order": asdict(limit_order),
        })
        order_data = json.dumps(req, cls=JSONEncoder)

        logger.info(f"create limit order: {order_data}")
        res = requests.post(url, headers=self.headers, data=order_data)

        if res.status_code == 201:
            data = res.json()
            logger.info(f"create limit order success: {data}")
            return parse_create_limit_order_response(data)
        else:
            logger.error(f"Error creating order: {res.status_code} {res.text}")
            return None

    def cancel_limit_order(self, order_id: str) -> CancelOrderResponse | None:
        url = f"{self.url}/v3/accounts/{self.account}/orders/{order_id}/cancel"

        logger.info(f"cancel order: {order_id=}")
        res = requests.put(url, headers=self.headers)

        if res.status_code == 200:
            data = res.json()
            logger.info(f"cancel limit order success: {data}")
            return parse_cancel_order_response(data)
        else:
            logger.error(f"Error canceling order: {res.status_code} {res.text}")
            return None

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from .common import OrderPositionFill, OrderTriggerCondition, TimeInForce
from .transaction import (
    ClientExtensions,
    LimitOrderTransaction,
    MarketOrderTransaction,
    OrderCancelTransaction,
    OrderFillTransaction,
    StopLossDetails,
    TakeProfitDetails,
    parse_limit_order_transaction,
    parse_market_order_transaction,
    parse_order_cancel_transaction,
    parse_order_fill_transaction,
)


# cf. https://developer.oanda.com/rest-live-v20/order-df/#OrderType
class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    MARKET_IF_TOUCHED = "MARKET_IF_TOUCHED"
    TAKE_PROFIT = "TAKE_PROFIT"
    STOP_LOSS = "STOP_LOSS"
    GUARANTEED_STOP_LOSS = "GUARANTEED_STOP_LOSS"
    TRAILING_STOP_LOSS = "TRAILING_STOP_LOSS"
    FIXED_PRICE = "FIXED_PRICE"


# cf. https://developer.oanda.com/rest-live-v20/order-df/#OrderState
class OrderState(Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    TRIGGERED = "TRIGGERED"
    CANCELLED = "CANCELLED"


# cf. https://developer.oanda.com/rest-live-v20/order-df/#MarketOrderRequest
@dataclass
class MarketOrderRequest:
    instrument: str
    units: Decimal
    type: OrderType = OrderType.MARKET
    time_in_force: TimeInForce = TimeInForce.FOK
    price_bound: Optional[Decimal] = None
    position_fill: OrderPositionFill = OrderPositionFill.DEFAULT
    client_extensions: Optional[ClientExtensions] = None
    take_profit_on_fill: Optional[TakeProfitDetails] = None
    stop_loss_on_fill: Optional[StopLossDetails] = None
    # guaranteed_stop_loss_on_fill: GuaranteedStopLossDetails
    # trailing_stop_loss_on_fill: TrailingStopLossDetails
    trade_client_extensions: Optional[ClientExtensions] = None


# cf. https://developer.oanda.com/rest-live-v20/order-df/#LimitOrderRequest
@dataclass
class LimitOrderRequest:
    instrument: str
    units: Decimal
    price: Decimal
    type: OrderType = OrderType.LIMIT
    time_in_force: TimeInForce = TimeInForce.GTC
    gtd_time: Optional[datetime] = None
    position_fill: OrderPositionFill = OrderPositionFill.DEFAULT
    trigger_condition: OrderTriggerCondition = OrderTriggerCondition.DEFAULT
    client_extensions: Optional[ClientExtensions] = None
    take_profit_on_fill: Optional[TakeProfitDetails] = None
    stop_loss_on_fill: Optional[StopLossDetails] = None
    # guaranteed_stop_loss_on_fill: GuaranteedStopLossDetails
    # trailing_stop_loss_on_fill: TrailingStopLossDetails
    trade_client_extensions: Optional[ClientExtensions] = None


# cf. https://developer.oanda.com/rest-live-v20/order-ep/
@dataclass
class CreateOrderResponse:
    related_transaction_ids: list[str]
    last_transaction_id: str


# cf. https://developer.oanda.com/rest-live-v20/order-ep/
@dataclass
class CreateMarketOrderResponse(CreateOrderResponse):
    order_create_transaction: MarketOrderTransaction
    order_fill_transaction: OrderFillTransaction


def parse_create_market_order_response(data: dict) -> CreateMarketOrderResponse:
    return CreateMarketOrderResponse(
        order_create_transaction=parse_market_order_transaction(data["orderCreateTransaction"]),
        order_fill_transaction=parse_order_fill_transaction(data["orderFillTransaction"]),
        related_transaction_ids=data["relatedTransactionIDs"],
        last_transaction_id=data["lastTransactionID"],
    )


# cf. https://developer.oanda.com/rest-live-v20/order-ep/
@dataclass
class CreateLimitOrderResponse(CreateOrderResponse):
    order_create_transaction: LimitOrderTransaction


def parse_create_limit_order_response(data: dict) -> CreateLimitOrderResponse:
    return CreateLimitOrderResponse(
        order_create_transaction=parse_limit_order_transaction(data["orderCreateTransaction"]),
        related_transaction_ids=data["relatedTransactionIDs"],
        last_transaction_id=data["lastTransactionID"],
    )


# cf. https://developer.oanda.com/rest-live-v20/order-ep/
@dataclass
class CancelOrderResponse(CreateOrderResponse):
    order_cancel_transaction: OrderCancelTransaction


def parse_cancel_order_response(data: dict) -> CancelOrderResponse:
    return CancelOrderResponse(
        order_cancel_transaction=parse_order_cancel_transaction(data["orderCancelTransaction"]),
        related_transaction_ids=data["relatedTransactionIDs"],
        last_transaction_id=data["lastTransactionID"],
    )

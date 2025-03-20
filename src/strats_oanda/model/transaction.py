from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from .common import OrderTriggerCondition, TimeInForce, parse_time


# cf. https://developer.oanda.com/rest-live-v20/transaction-df/#ClientExtensions
@dataclass
class ClientExtensions:
    id: str
    tag: str
    comment: str


# cf. https://developer.oanda.com/rest-live-v20/transaction-df/#TakeProfitDetails
@dataclass
class TakeProfitDetails:
    price: Decimal
    time_in_force: TimeInForce = TimeInForce.GTC
    gtd_time: Optional[datetime] = None
    client_extensions: Optional[ClientExtensions] = None


# cf. https://developer.oanda.com/rest-live-v20/transaction-df/#StopLossDetails
@dataclass
class StopLossDetails:
    price: Decimal | None = None
    distance: Decimal | None = None
    time_in_force: TimeInForce = TimeInForce.GTC
    gtd_time: datetime | None = None
    client_extensions: ClientExtensions | None = None


# https://developer.oanda.com/rest-live-v20/transaction-df/#LimitOrderReason
class LimitOrderReason(Enum):
    CLIENT_ORDER = "CLIENT_ORDER"
    REPLACEMENT = "REPLACEMENT"


# https://developer.oanda.com/rest-live-v20/transaction-df/#OrderCancelReason
class OrderCancelReason(Enum):
    CLIENT_REQUEST = "CLIENT_REQUEST"
    # ...


# https://developer.oanda.com/rest-live-v20/transaction-df/#OrderFillReason
class OrderFillReason(Enum):
    LIMIT_ORDER = "LIMIT_ORDER"
    # ...


# cf. https://developer.oanda.com/rest-live-v20/transaction-df/#OrderFillTransaction
@dataclass
class Transaction:
    id: str
    time: datetime
    user_id: int
    account_id: str
    batch_id: str
    type: str
    request_id: str  # allow empty string


# type = LIMIT_ORDER
# cf. https://developer.oanda.com/rest-live-v20/transaction-df/#LimitOrderTransaction
@dataclass
class LimitOrderTransaction(Transaction):
    instrument: str
    units: Decimal
    price: Decimal
    time_in_force: TimeInForce
    gtd_time: Optional[datetime]
    trigger_condition: OrderTriggerCondition
    reason: LimitOrderReason


def parse_limit_order_transaction(data: dict) -> LimitOrderTransaction:
    return LimitOrderTransaction(
        id=data["id"],
        time=parse_time(data["time"]),
        user_id=data["userID"],
        account_id=data["accountID"],
        batch_id=data["batchID"],
        request_id=data["requestID"],
        type=data["type"],
        instrument=data["instrument"],
        units=Decimal(data["units"]),
        price=Decimal(data["price"]),
        time_in_force=TimeInForce(data["timeInForce"]),
        gtd_time=parse_time(data["gtdTime"]) if "gtdTime" in data else None,
        trigger_condition=OrderTriggerCondition(data["triggerCondition"]),
        reason=LimitOrderReason(data["reason"]),
    )


# cf. https://developer.oanda.com/rest-live-v20/transaction-df/#OrderCancelTransaction
@dataclass
class OrderCancelTransaction(Transaction):
    order_id: str
    reason: OrderCancelReason
    client_order_id: str | None = None
    replaced_by_order_id: str | None = None


def parse_order_cancel_transaction(data: dict) -> OrderCancelTransaction:
    return OrderCancelTransaction(
        id=data["id"],
        time=parse_time(data["time"]),
        user_id=data["userID"],
        account_id=data["accountID"],
        batch_id=data["batchID"],
        request_id=data["requestID"],
        type=data["type"],
        order_id=data["orderID"],
        reason=OrderCancelReason(data["reason"]),
    )


# https://developer.oanda.com/rest-live-v20/transaction-df/#TradeOpen
@dataclass
class TradeOpen:
    trade_id: str
    units: Decimal
    price: Decimal
    # guaranteedExecutionFee: Decimal
    # quoteGuaranteedExecutionFee: Decimal
    half_spread_cost: Decimal
    initial_margin_required: Decimal
    client_extensions: ClientExtensions | None = None


def parse_trade_open(data: dict) -> TradeOpen:
    return TradeOpen(
        trade_id=data["tradeID"],
        units=Decimal(data["units"]),
        price=Decimal(data["price"]),
        half_spread_cost=Decimal(data["halfSpreadCost"]),
        initial_margin_required=Decimal(data["initialMarginRequired"]),
    )


# https://developer.oanda.com/rest-live-v20/transaction-df/#TradeReduce
@dataclass
class TradeReduce:
    trade_id: str
    units: Decimal
    price: Decimal
    # ...


def parse_trade_reduce(data: dict) -> TradeReduce:
    return TradeReduce(
        trade_id=data["tradeID"],
        units=Decimal(data["units"]),
        price=Decimal(data["price"]),
    )


# https://developer.oanda.com/rest-live-v20/transaction-df/#OrderFillTransaction
@dataclass
class OrderFillTransaction(Transaction):
    order_id: str
    instrument: str
    units: Decimal
    requested_units: Decimal
    account_balance: Decimal
    half_spread_cost: Decimal
    reason: OrderFillReason
    client_order_id: str | None = None
    trade_opened: TradeOpen | None = None
    trades_closed: list[TradeReduce] | None = None
    trade_reduced: TradeReduce | None = None


def parse_order_fill_transaction(data: dict) -> OrderFillTransaction:
    return OrderFillTransaction(
        id=data["id"],
        account_id=data["accountID"],
        user_id=data["userID"],
        batch_id=data["batchID"],
        request_id=data["requestID"] if "requestID" in data else "",
        time=parse_time(data["time"]),
        type=data["type"],
        order_id=data["orderID"],
        client_order_id=data["clientOrderID"] if "clientOrderID" in data else None,
        instrument=data["instrument"],
        units=Decimal(data["units"]),
        requested_units=Decimal(data["requestedUnits"]),
        account_balance=Decimal(data["accountBalance"]),
        half_spread_cost=Decimal(data["halfSpreadCost"]),
        reason=OrderFillReason(data["reason"]),
        trade_opened=parse_trade_open(data["tradeOpened"]) if "tradeOpened" in data else None,
        trades_closed=[parse_trade_reduce(x) for x in data["tradeClosed"]]
        if "tradeClosed" in data
        else None,
        trade_reduced=parse_trade_reduce(data["tradeReduced"]) if "tradeReduced" in data else None,
    )

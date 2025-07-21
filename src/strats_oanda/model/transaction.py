from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from ..helper import parse_time
from .common import (
    HomeConversionFactors,
    OrderPositionFill,
    OrderTriggerCondition,
    TimeInForce,
    parse_home_conversion_factors,
)
from .pricing import ClientPrice, parse_client_price


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
    price: Optional[Decimal] = None
    distance: Optional[Decimal] = None
    time_in_force: TimeInForce = TimeInForce.GTC
    gtd_time: Optional[datetime] = None
    client_extensions: Optional[ClientExtensions] = None


# https://developer.oanda.com/rest-live-v20/transaction-df/#MarketOrderReason
class MarketOrderReason(Enum):
    CLIENT_ORDER = "CLIENT_ORDER"
    TRADE_CLOSE = "TRADE_CLOSE"
    POSITION_CLOSEOUT = "POSITION_CLOSEOUT"
    MARGIN_CLOSEOUT = "MARGIN_CLOSEOUT"
    DELAYED_TRADE_CLOSEOUT = "DELAYED_TRADE_CLOSEOUT"


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
    STOP_ORDER = "STOP_ORDER"
    MARKET_IF_TOUCHED_ORDER = "MARKET_IF_TOUCHED_ORDER"
    TAKE_PROFIT_ORDER = "TAKE_PROFIT_ORDER"
    STOP_LOSS_ORDER = "STOP_LOSS_ORDER"
    GUARANTEED_STOP_LOSS_ORDER = "GUARANTEED_STOP_LOSS_ORDER"
    TRAILING_STOP_LOSS_ORDER = "TRAILING_STOP_LOSS_ORDER"
    MARKET_ORDER = "MARKET_ORDER"
    MARKET_ORDER_TRADE_CLOSE = "MARKET_ORDER_TRADE_CLOSE"
    MARKET_ORDER_POSITION_CLOSEOUT = "MARKET_ORDER_POSITION_CLOSEOUT"
    MARKET_ORDER_MARGIN_CLOSEOUT = "MARKET_ORDER_MARGIN_CLOSEOUT"
    MARKET_ORDER_DELAYED_TRADE_CLOSE = "MARKET_ORDER_DELAYED_TRADE_CLOSE"
    FIXED_PRICE_ORDER = "FIXED_PRICE_ORDER"
    FIXED_PRICE_ORDER_PLATFORM_ACCOUNT_MIGRATION = "FIXED_PRICE_ORDER_PLATFORM_ACCOUNT_MIGRATION"
    FIXED_PRICE_ORDER_DIVISION_ACCOUNT_MIGRATION = "FIXED_PRICE_ORDER_DIVISION_ACCOUNT_MIGRATION"
    FIXED_PRICE_ORDER_ADMINISTRATIVE_ACTION = "FIXED_PRICE_ORDER_ADMINISTRATIVE_ACTION"


# cf. https://developer.oanda.com/rest-live-v20/transaction-df/#MarketOrderTradeClose
@dataclass
class MarketOrderTradeClose:
    trade_id: str
    client_trade_id: str
    units: Decimal


# cf. https://developer.oanda.com/rest-live-v20/transaction-df/#MarketOrderPositionCloseout
@dataclass
class MarketOrderPositionCloseout:
    instrument: str
    units: Decimal


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
    client_extensions: Optional[ClientExtensions] = None


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


# type = MARKET_ORDER
# cf. https://developer.oanda.com/rest-live-v20/transaction-df/#MarketOrderTransaction
@dataclass
class MarketOrderTransaction(Transaction):
    instrument: str
    units: Decimal
    time_in_force: TimeInForce
    reason: MarketOrderReason
    price_bound: Optional[Decimal] = None
    position_fill: OrderPositionFill = OrderPositionFill.DEFAULT
    trade_close: Optional[MarketOrderTradeClose] = None
    long_position_closeout: Optional[MarketOrderPositionCloseout] = None
    short_position_closeout: Optional[MarketOrderPositionCloseout] = None
    # margin_closeout: Optional[] = None
    # delayed_trade_close: Optional[] = None
    client_extensions: Optional[ClientExtensions] = None
    trade_client_extensions: Optional[ClientExtensions] = None
    # take_profit_on_fill
    # stop_loss_on_fill
    # trailing_stop_loss_on_fill
    # guarantee_stop_loss_on_fill


def parse_market_order_transaction(data: dict) -> MarketOrderTransaction:
    return MarketOrderTransaction(
        id=data["id"],
        time=parse_time(data["time"]),
        user_id=data["userID"],
        account_id=data["accountID"],
        batch_id=data["batchID"],
        request_id=data["requestID"],
        type=data["type"],
        instrument=data["instrument"],
        units=Decimal(data["units"]),
        time_in_force=TimeInForce(data["timeInForce"]),
        price_bound=Decimal(data["price_bound"]) if "price_bound" in data else None,
        reason=MarketOrderReason(data["reason"]),
    )


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
    client_order_id: Optional[str] = None
    replaced_by_order_id: Optional[str] = None


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


# cf. https://developer.oanda.com/rest-live-v20/transaction-df/#OrderFillTransaction
@dataclass
class OrderFillTransaction(Transaction):
    order_id: str
    client_order_id: Optional[str]
    instrument: str
    units: Decimal
    home_conversion_factors: HomeConversionFactors
    # Full Volume Weighted Average Price
    full_vwap: Decimal
    full_price: ClientPrice
    reason: OrderFillReason
    pl: Decimal
    quote_pl: Decimal
    financing: Decimal
    base_financing: Decimal
    quote_financing: Optional[Decimal]
    commission: Decimal
    guaranteed_execution_fee: Decimal
    quote_guaranteed_execution_fee: Decimal
    account_balance: Decimal
    trade_opened: Optional[TradeOpen]
    trades_closed: Optional[list[TradeReduce]]
    trade_reduced: Optional[TradeReduce]
    half_spread_cost: Decimal


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
        home_conversion_factors=parse_home_conversion_factors(data["homeConversionFactors"]),
        full_vwap=Decimal(data["fullVWAP"]),
        full_price=parse_client_price(data["fullPrice"]),
        reason=OrderFillReason(data["reason"]),
        pl=Decimal(data["pl"]),
        quote_pl=Decimal(data["quotePL"]),
        financing=Decimal(data["financing"]),
        base_financing=Decimal(data["baseFinancing"]),
        quote_financing=Decimal(data["quoteFinancing"]) if "quoteFinancing" in data else None,
        commission=Decimal(data["commission"]),
        guaranteed_execution_fee=Decimal(data["guaranteedExecutionFee"]),
        quote_guaranteed_execution_fee=Decimal(data["quoteGuaranteedExecutionFee"]),
        account_balance=Decimal(data["accountBalance"]),
        trade_opened=parse_trade_open(data["tradeOpened"]) if "tradeOpened" in data else None,
        trades_closed=[parse_trade_reduce(x) for x in data["tradeClosed"]]
        if "tradeClosed" in data
        else None,
        trade_reduced=parse_trade_reduce(data["tradeReduced"]) if "tradeReduced" in data else None,
        half_spread_cost=Decimal(data["halfSpreadCost"]),
    )

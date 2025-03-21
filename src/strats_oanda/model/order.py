from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from .common import OrderTriggerCondition, TimeInForce
from .transaction import ClientExtensions, StopLossDetails, TakeProfitDetails


# cf. https://developer.oanda.com/rest-live-v20/order-df/#OrderType
class OrderType(Enum):
    LIMIT = "LIMIT"

    # When the last traded price touches the trigger price,
    # the take profit order will execute immediately as a market order
    # cf. https://support.kraken.com/hc/en-us/articles/8407751019284-Take-profit-orders
    TAKE_PROFIT = "TAKE_PROFIT"


# cf. https://developer.oanda.com/rest-live-v20/order-df/#OrderState
class OrderState(Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    TRIGGERED = "TRIGGERED"
    CANCELLED = "CANCELLED"


# cf. https://developer.oanda.com/rest-live-v20/order-df/#OrderPositionFill
class OrderPositionFill(Enum):
    OPEN_ONLY = "OPEN_ONLY"
    REDUCE_FIRST = "REDUCE_FIRST"
    REDUCE_ONLY = "REDUCE_ONLY"
    DEFAULT = "DEFAULT"


# cf. https://developer.oanda.com/rest-live-v20/order-df/#LimitOrderRequest
@dataclass
class LimitOrderRequest:
    instrument: str
    units: Decimal
    price: Decimal
    type: OrderType = OrderType.LIMIT
    timeInForce: TimeInForce = TimeInForce.GTC
    gtdTime: Optional[datetime] = None
    positionFill: OrderPositionFill = OrderPositionFill.DEFAULT
    triggerCondition: OrderTriggerCondition = OrderTriggerCondition.DEFAULT
    clientExtensions: Optional[ClientExtensions] = None
    takeProfitOnFill: Optional[TakeProfitDetails] = None
    stopLossOnFill: Optional[StopLossDetails] = None
    # guaranteedStopLossOnFill: GuaranteedStopLossDetails
    # trailingStopLossOnFill: TrailingStopLossDetails
    tradeClientExtensions: Optional[ClientExtensions] = None

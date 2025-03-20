from enum import Enum
from datetime import datetime


# cf. https://developer.oanda.com/rest-live-v20/order-df/#TimeInForce
class TimeInForce(Enum):
    GTC = "GTC"  # Good until Cancelled
    GTD = "GTD"  # Good until Date


# cf. https://developer.oanda.com/rest-live-v20/order-df/#OrderTriggerCondition
class OrderTriggerCondition(Enum):
    DEFAULT = "DEFAULT"
    # ...


def parse_time(time: str) -> datetime:
    time_str = time.replace("Z", "+00:00")
    return datetime.fromisoformat(time_str)

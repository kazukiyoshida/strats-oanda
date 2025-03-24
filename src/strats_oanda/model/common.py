from enum import Enum


# cf. https://developer.oanda.com/rest-live-v20/order-df/#TimeInForce
class TimeInForce(Enum):
    GTC = "GTC"  # Good until Cancelled
    GTD = "GTD"  # Good until Date


# cf. https://developer.oanda.com/rest-live-v20/order-df/#OrderTriggerCondition
class OrderTriggerCondition(Enum):
    DEFAULT = "DEFAULT"
    # ...

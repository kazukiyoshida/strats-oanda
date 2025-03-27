from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


# cf. https://developer.oanda.com/rest-live-v20/order-df/#TimeInForce
class TimeInForce(Enum):
    GTC = "GTC"  # Good until Cancelled
    GTD = "GTD"  # Good until Date
    GFD = "GFD"  # Good For Day
    FOK = "FOK"  # Filled Or Killed
    IOC = "IOC"  # Immediately partially filled Or Cancelled


# cf. https://developer.oanda.com/rest-live-v20/order-df/#OrderTriggerCondition
class OrderTriggerCondition(Enum):
    DEFAULT = "DEFAULT"
    # ...


# cf. https://developer.oanda.com/rest-live-v20/order-df/#OrderPositionFill
class OrderPositionFill(Enum):
    OPEN_ONLY = "OPEN_ONLY"
    REDUCE_FIRST = "REDUCE_FIRST"
    REDUCE_ONLY = "REDUCE_ONLY"
    DEFAULT = "DEFAULT"


# cf. https://developer.oanda.com/rest-live-v20/primitives-df/#HomeConversionFactors
@dataclass
class HomeConversionFactors:
    gain_quote_home: Decimal
    loss_quote_home: Decimal
    gain_base_home: Decimal
    loss_base_home: Decimal


def parse_home_conversion_factors(data: dict) -> HomeConversionFactors:
    return HomeConversionFactors(
        gain_quote_home=data["gainQuoteHome"],
        loss_quote_home=data["lossQuoteHome"],
        gain_base_home=data["gainBaseHome"],
        loss_base_home=data["lossBaseHome"],
    )

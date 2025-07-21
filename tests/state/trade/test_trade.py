import asyncio
from decimal import Decimal

import pytest

import strats_oanda
from strats_oanda.client import OrderClient
from strats_oanda.model import (
    MarketOrderRequest,
    OrderPositionFill,
)
from strats_oanda.state import Trade

INSTRUMENT = "USD_JPY"
UNITS = Decimal("1")


@pytest.mark.asyncio
async def test_create_market_trade():
    print("!!! THERE ARE API CALLS IN OANDA PRACTICE ENVIRONMENT !!!")

    file_path = ".strats_oanda_practice.yaml"
    strats_oanda.basic_config(use_file=True, file_path=file_path)

    trade = Trade(order_client=OrderClient())
    assert trade.id == 0

    await trade.session_open()

    # Entry
    transaction = await trade.create_market_order(
        MarketOrderRequest(
            instrument=INSTRUMENT,
            units=UNITS,
        )
    )
    assert transaction.units == UNITS
    assert transaction.pl == Decimal("0")
    assert len(trade.transactions) == 1

    await asyncio.sleep(2)

    # Exit
    transaction = await trade.create_market_order(
        MarketOrderRequest(
            instrument=INSTRUMENT,
            units=UNITS * -1,
            position_fill=OrderPositionFill.REDUCE_ONLY,
        )
    )
    assert transaction.units == UNITS * -1
    assert len(trade.transactions) == 2

    assert trade.total_profit < Decimal("0")  # market order should lose money
    assert trade.net_units == Decimal("0")

    await trade.session_close()

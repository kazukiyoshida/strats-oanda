import asyncio
from decimal import Decimal

# from dataclasses import asdict
# from pprint import pprint
import pytest

import strats_oanda
from strats_oanda.client import OrderClient
from strats_oanda.model import MarketOrderRequest, OrderPositionFill

INSTRUMENT = "USD_JPY"
UNITS = Decimal("1")


@pytest.mark.skip(reason="THERE ARE API CALLS IN OANDA PRACTICE ENVIRONMENT")
@pytest.mark.asyncio
async def test_order_client():
    print("!!! THERE ARE API CALLS IN OANDA PRACTICE ENVIRONMENT !!!")

    file_path = ".strats_oanda_practice.yaml"
    strats_oanda.basic_config(use_file=True, file_path=file_path)

    async with OrderClient() as client:
        result = await client.create_market_order(
            MarketOrderRequest(
                instrument=INSTRUMENT,
                units=UNITS,
            )
        )
        # print("# ENTRY")
        # pprint(asdict(result))
        assert result.order_create_transaction.instrument == "USD_JPY"
        assert result.order_create_transaction.type == "MARKET_ORDER"
        assert result.order_fill_transaction.trade_opened.units == UNITS

        await asyncio.sleep(2)

        # cleanup
        result = await client.create_market_order(
            MarketOrderRequest(
                instrument=INSTRUMENT,
                units=UNITS * -1,
                position_fill=OrderPositionFill.REDUCE_ONLY,
            )
        )
        # print("# EXIT")
        # pprint(asdict(result))

from datetime import datetime, timezone
from decimal import Decimal

from strats_oanda.model import (
    ClientPrice,
    CreateMarketOrderResponse,
    HomeConversionFactors,
    MarketOrderReason,
    MarketOrderTransaction,
    OrderFillReason,
    OrderFillTransaction,
    OrderPositionFill,
    PriceBucket,
    TimeInForce,
    TradeOpen,
    parse_create_market_order_response,
)


def test_parse_create_market_order_response():
    data = {
        "lastTransactionID": "79",
        "orderCreateTransaction": {
            "accountID": "101-009-31084545-001",
            "batchID": "78",
            "id": "78",
            "instrument": "USD_JPY",
            "positionFill": "DEFAULT",
            "reason": "CLIENT_ORDER",
            "requestID": "79368596638985858",
            "time": "2025-03-27T12:34:11.874521250Z",
            "timeInForce": "FOK",
            "type": "MARKET_ORDER",
            "units": "1",
            "userID": 31084545,
        },
        "orderFillTransaction": {
            "accountBalance": "3000000.0150",
            "accountID": "101-009-31084545-001",
            "baseFinancing": "0",
            "batchID": "78",
            "commission": "0.0000",
            "financing": "0.0000",
            "fullPrice": {
                "asks": [{"liquidity": "250000", "price": "150.763"}],
                "bids": [{"liquidity": "250000", "price": "150.759"}],
                "closeoutAsk": "150.769",
                "closeoutBid": "150.753",
                "timestamp": "2025-03-27T12:34:11.618910233Z",
            },
            "fullVWAP": "150.763",
            "gainQuoteHomeConversionFactor": "1",
            "guaranteedExecutionFee": "0.0000",
            "halfSpreadCost": "0.0020",
            "homeConversionFactors": {
                "gainBaseHome": {"factor": "150.459478"},
                "gainQuoteHome": {"factor": "1"},
                "lossBaseHome": {"factor": "151.062522"},
                "lossQuoteHome": {"factor": "1"},
            },
            "id": "79",
            "instrument": "USD_JPY",
            "lossQuoteHomeConversionFactor": "1",
            "orderID": "78",
            "pl": "0.0000",
            "price": "150.763",
            "quoteGuaranteedExecutionFee": "0",
            "quotePL": "0",
            "reason": "MARKET_ORDER",
            "requestID": "79368596638985858",
            "requestedUnits": "1",
            "time": "2025-03-27T12:34:11.874521250Z",
            "tradeOpened": {
                "guaranteedExecutionFee": "0.0000",
                "halfSpreadCost": "0.0020",
                "initialMarginRequired": "6.0304",
                "price": "150.763",
                "quoteGuaranteedExecutionFee": "0",
                "tradeID": "79",
                "units": "1",
            },
            "type": "ORDER_FILL",
            "units": "1",
            "userID": 31084545,
        },
        "relatedTransactionIDs": ["78", "79"],
    }
    got = parse_create_market_order_response(data)
    expect = CreateMarketOrderResponse(
        related_transaction_ids=["78", "79"],
        last_transaction_id="79",
        order_create_transaction=MarketOrderTransaction(
            id="78",
            time=datetime(2025, 3, 27, 12, 34, 11, 874521, tzinfo=timezone.utc),
            user_id=31084545,
            account_id="101-009-31084545-001",
            batch_id="78",
            type="MARKET_ORDER",
            request_id="79368596638985858",
            instrument="USD_JPY",
            units=Decimal("1"),
            time_in_force=TimeInForce.FOK,
            reason=MarketOrderReason.CLIENT_ORDER,
            price_bound=None,
            position_fill=OrderPositionFill.DEFAULT,
            trade_close=None,
            long_position_closeout=None,
            short_position_closeout=None,
            client_extensions=None,
            trade_client_extensions=None,
        ),
        order_fill_transaction=OrderFillTransaction(
            id="79",
            time=datetime(2025, 3, 27, 12, 34, 11, 874521, tzinfo=timezone.utc),
            user_id=31084545,
            account_id="101-009-31084545-001",
            batch_id="78",
            type="ORDER_FILL",
            request_id="79368596638985858",
            order_id="78",
            client_order_id=None,
            instrument="USD_JPY",
            units=Decimal("1"),
            home_conversion_factors=HomeConversionFactors(
                gain_quote_home={"factor": "1"},
                loss_quote_home={"factor": "1"},
                gain_base_home={"factor": "150.459478"},
                loss_base_home={"factor": "151.062522"},
            ),
            full_vwap=Decimal("150.763"),
            full_price=ClientPrice(
                type="PRICE",
                instrument=None,
                timestamp=datetime(2025, 3, 27, 12, 34, 11, 618910, tzinfo=timezone.utc),
                tradeable=None,
                bids=[PriceBucket(price=Decimal("150.759"), liquidity="250000")],
                asks=[PriceBucket(price=Decimal("150.763"), liquidity="250000")],
                closeout_bid=Decimal("150.753"),
                closeout_ask=Decimal("150.769"),
            ),
            reason=OrderFillReason.MARKET_ORDER,
            pl=Decimal("0.0000"),
            quote_pl=Decimal("0"),
            financing=Decimal("0.0000"),
            base_financing=Decimal("0"),
            quote_financing=None,
            commission=Decimal("0.0000"),
            guaranteed_execution_fee=Decimal("0.0000"),
            quote_guaranteed_execution_fee=Decimal("0"),
            account_balance=Decimal("3000000.0150"),
            trade_opened=TradeOpen(
                trade_id="79",
                units=Decimal("1"),
                price=Decimal("150.763"),
                half_spread_cost=Decimal("0.0020"),
                initial_margin_required=Decimal("6.0304"),
                client_extensions=None,
            ),
            trades_closed=None,
            trade_reduced=None,
            half_spread_cost=Decimal("0.0020"),
        ),
    )
    assert got == expect

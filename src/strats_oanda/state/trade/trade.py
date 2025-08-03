import logging
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from strats_oanda.client import OrderClient
from strats_oanda.model import (
    LimitOrderRequest,
    MarketOrderRequest,
    OrderFillTransaction,
    OrderPositionFill,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Transaction:
    id: str
    order_id: str
    units: Decimal
    price: Decimal
    time: datetime
    pl: Optional[Decimal] = None
    tags: Optional[dict] = None


@dataclass
class LimitOrder:
    id: str
    units: Decimal
    price: Decimal
    time: datetime
    position_fill: OrderPositionFill
    tags: Optional[dict] = None


class Trade:
    _counter = 0

    def __init__(self, order_client: OrderClient):
        self.order_client = order_client

        self.limit_orders: dict[str, LimitOrder] = {}
        self.transactions: dict[str, Transaction] = {}

        # Trade ID
        self.id = type(self)._counter
        type(self)._counter += 1

    async def session_open(self):
        await self.order_client.open()

    async def session_close(self):
        await self.order_client.close()

    async def create_market_order(
        self,
        request: MarketOrderRequest,
        tags: Optional[dict] = None,
    ) -> Transaction:
        result = await self.order_client.create_market_order(request)
        tx = result.order_fill_transaction
        transaction = Transaction(
            id=tx.id,
            order_id=tx.order_id,
            units=tx.units,
            price=tx.full_vwap,
            time=tx.time,
            pl=tx.pl,
            tags=tags,
        )
        self.transactions[tx.id] = transaction
        return transaction

    async def create_limit_order(
        self,
        request: LimitOrderRequest,
        tags: Optional[dict] = None,
    ) -> LimitOrder:
        result = await self.order_client.create_limit_order(request)
        tx = result.order_create_transaction
        limit_order = LimitOrder(
            id=tx.id,
            units=tx.units,
            price=tx.price,
            time=tx.time,
            position_fill=request.position_fill,
            tags=tags,
        )
        self.limit_orders[tx.id] = limit_order
        return limit_order

    async def cancel_limit_order(self, order_id: str) -> str:
        if order_id not in self.limit_orders:
            raise ValueError(f"order_id `{order_id}` is not found")
        await self.order_client.cancel_limit_order(order_id)
        del self.limit_orders[order_id]
        return order_id

    def notify_execution(self, tx: OrderFillTransaction):
        if tx.order_id not in self.limit_orders:
            logger.warning(f"order_id `{tx.order_id}` is not found")
            return

        limit_order = self.limit_orders[tx.order_id]
        transaction = Transaction(
            id=tx.id,
            order_id=tx.order_id,
            units=tx.units,
            price=tx.full_vwap,
            time=tx.time,
            pl=tx.pl,
            tags=limit_order.tags,  # inherit the tags from limit_order
        )
        self.transactions[tx.id] = transaction

        # Order filled completely
        if limit_order.units == tx.units:
            del self.limit_orders[tx.order_id]
        # Order filled partialy
        else:
            limit_order.units -= tx.units
            self.limit_orders[tx.order_id] = limit_order

    @property
    def total_profit(self) -> Decimal:
        total = Decimal("0")
        for transaction in self.transactions.values():
            if transaction.pl is not None:
                total += transaction.pl
        return total

    @property
    def net_units(self) -> Decimal:
        total = Decimal("0")
        for transaction in self.transactions.values():
            total += transaction.units
        return total


def transaction_to_trade(tx, trade):
    if isinstance(tx, OrderFillTransaction):
        trade.notify_execution(tx)
    return trade

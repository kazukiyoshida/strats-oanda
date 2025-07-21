from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from strats_oanda.client import OrderClient
from strats_oanda.model import (
    LimitOrderRequest,
    MarketOrderRequest,
)


@dataclass
class Transaction:
    id: str
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
    is_entry: bool
    tags: Optional[dict] = None


class Trade:
    _counter = 0

    def __init__(self, order_client: OrderClient):
        self.order_client = order_client

        self.limit_order: dict[str, LimitOrder] = {}
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
            units=tx.units,
            price=tx.full_vwap,
            time=tx.time,
            pl=tx.pl,
            tags=tags,
        )
        self.transactions[tx.id] = transaction
        return transaction

    async def create_limit_order(self, limit_order: LimitOrderRequest) -> LimitOrder:
        raise NotImplementedError("")

    async def cancel_limit_order(self, order_id: str) -> str:
        raise NotImplementedError("")

    def notify_execution(self):
        raise NotImplementedError("")

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

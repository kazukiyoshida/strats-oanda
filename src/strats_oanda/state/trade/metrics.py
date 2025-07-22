from prometheus_client import Counter, Gauge

from .trade import Trade


class TradeMetrics:
    def __init__(self, name: str):
        self.total_profit = Gauge(f"{name}_total_profit", "")
        self.net_units = Gauge(f"{name}_net_units", "")
        self.limit_order_count = Counter(f"{name}_limit_order_count", "")
        self.transaction_count = Counter(f"{name}_transaction_count", "")


def trade_to_trade_metrics(trade: Trade, metrics: TradeMetrics):
    pass

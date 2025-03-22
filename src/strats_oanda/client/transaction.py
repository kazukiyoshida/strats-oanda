"""
Transaction Stream Endpoints
cf. https://developer.oanda.com/rest-live-v20/transaction-ep/
"""

import json
import threading
from queue import Queue

import requests

from strats_oanda.config import get_config
from strats_oanda.model.transaction import (
    parse_limit_order_transaction,
    parse_order_cancel_transaction,
    parse_order_fill_transaction,
)


class TransactionClient:
    def __init__(self):
        self.config = get_config()
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._transaction_stream, daemon=True)

    @property
    def is_alive(self) -> bool:
        return self.thread.is_alive()

    def start(self, queue: Queue):
        if not self.is_alive:
            self.queue = queue
            self.thread.start()

    def stop(self):
        if self.is_alive:
            self.stop_event.set()
            self.thread.join()

    def _transaction_stream(self):
        url = f"{self.url}/v3/accounts/{self.account}/transactions/stream"
        headers = {
            "Authorization": f"Bearer {self.token}",
        }
        with requests.get(url, headers=headers, stream=True) as res:
            for line in res.iter_lines():
                if self.stop_event.is_set():
                    return
                if line:
                    json_str = line.decode("utf-8")
                    data = json.loads(json_str)
                    tx_type = data.get("type")

                    if tx_type == "LIMIT_ORDER":
                        tx = parse_limit_order_transaction(data)
                    elif tx_type == "ORDER_CANCEL":
                        tx = parse_order_cancel_transaction(data)
                    elif tx_type == "ORDER_FILL":
                        tx = parse_order_fill_transaction(data)
                    elif tx_type == "HEARTBEAT":
                        continue
                    else:
                        continue

                    self.notification_queue.put(tx)

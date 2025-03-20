# Transaction Stream Endpoints
# cf. https://developer.oanda.com/rest-live-v20/transaction-ep/
import json
import threading
import queue
import requests

from strats_oanda.logger import logger
from strats_oanda.model.transaction import \
    parse_limit_order_transaction, \
    parse_order_cancel_transaction, \
    parse_order_fill_transaction


class TransactionClient:
    def __init__(self, url, account, token, notification_queue: queue.Queue):
        self.url = url
        self.account = account
        self.token = token
        self.notification_queue = notification_queue
        self.thread = threading.Thread(target=self._transaction_stream, daemon=True)
        self.stop_event = threading.Event()

    def start_transaction_stream(self):
        self.thread.start()

    def stop_transaction_stream(self):
        self.stop_event.set()

    def _transaction_stream(self):
        url = f"{self.url}/v3/accounts/{self.account}/transactions/stream"
        headers = {
            "Authorization": f"Bearer {self.token}",
        }
        logger.info("start transaction streaming")
        with requests.get(url, headers=headers, stream=True) as res:
            for line in res.iter_lines():
                if self.stop_event.is_set():
                    logger.info("stop transaction streaming")
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
                        logger.warning(f"Ignored transaction type: {tx_type}, json: {json_str}")
                        continue

                    self.notification_queue.put(tx)

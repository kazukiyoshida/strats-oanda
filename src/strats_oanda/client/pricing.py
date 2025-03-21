"""
Pricing Stream Endpoints
cf. https://developer.oanda.com/rest-live-v20/pricing-ep/
"""

import json
from queue import Queue
from threading import Event, Thread

import requests

from strats_oanda.config import get_config
from strats_oanda.model.pricing import parse_client_price


class PricingStreamClient:
    def __init__(
        self,
        instruments: list[str],
    ):
        if not isinstance(instruments, list):
            raise ValueError(f"instruments must be list: {instruments}")

        self.config = get_config()
        self.instruments = instruments
        self.stop_event = Event()
        self.thread = Thread(target=self._pricing_stream, daemon=True)

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

    def _pricing_stream(self):
        url = f"{self.config.streaming_url}/v3/accounts/{self.config.account}/pricing/stream"
        params = {"instruments": ",".join(self.instruments)}
        headers = {
            "Authorization": f"Bearer {self.config.token}",
            "Accept-Datetime-Format": "RFC3339",
        }
        with requests.get(url, headers=headers, params=params, stream=True) as res:
            for line in res.iter_lines():
                if self.stop_event.is_set():
                    return
                if line:
                    json_str = line.decode("utf-8")
                    if "HEARTBEAT" in json_str:
                        continue

                    data = json.loads(json_str)
                    price = parse_client_price(data)
                    self.queue.put(price)

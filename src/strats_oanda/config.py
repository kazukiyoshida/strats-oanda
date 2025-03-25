import os
import threading
import warnings
from pathlib import Path

import yaml


class OANDAConfig:
    def __init__(self):
        self._lock = threading.Lock()
        self._initialized = False
        self.rest_url = None
        self.streaming_url = None
        self.account = None
        self.token = None

    def configure(
        self,
        *,
        rest_url=None,
        streaming_url=None,
        account=None,
        token=None,
        force=False,
    ):
        with self._lock:
            if self._initialized and not force:
                warnings.warn(
                    "APIConfig is already configured. Use force=True to override.",
                    stacklevel=2,
                )
                return

            self.rest_url = rest_url
            self.streaming_url = streaming_url
            self.account = account
            self.token = token
            self._initialized = True

    def load_from_env(self):
        self.configure(
            rest_url=os.getenv("OANDA_REST_URL"),
            streaming_url=os.getenv("OANDA_STREAMING_URL"),
            account=os.getenv("OANDA_ACCOUNT"),
            token=os.getenv("OANDA_TOKEN"),
        )

    def load_from_file(self, path=None):
        if path is None:
            path = Path.home() / ".strats_oanda.yaml"

        if not Path(path).exists():
            warnings.warn(f"Config file not found: {path}", stacklevel=2)
            return

        with open(path) as f:
            data = yaml.safe_load(f)

        self.configure(
            rest_url=data.get("rest_url"),
            streaming_url=data.get("streaming_url"),
            account=data.get("account"),
            token=data.get("token"),
        )

    def is_configured(self):
        return self._initialized

    @property
    def account_rest_url(self) -> str:
        return f"{self.rest_url}/v3/accounts/{self.account}"

    @property
    def account_streaming_url(self) -> str:
        return f"{self.streaming_url}/v3/accounts/{self.account}"


_config = OANDAConfig()


def basic_config(
    *,
    rest_url=None,
    streaming_url=None,
    account=None,
    token=None,
    force=False,
    use_env=False,
    use_file=False,
    file_path=None,
):
    if use_env:
        _config.load_from_env()
    elif use_file:
        _config.load_from_file(file_path)
    else:
        _config.configure(
            rest_url=rest_url,
            streaming_url=streaming_url,
            account=account,
            token=token,
            force=force,
        )


def get_config() -> OANDAConfig:
    return _config

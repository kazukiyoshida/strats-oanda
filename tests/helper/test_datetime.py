from datetime import datetime

from strats_oanda.helper import format_datetime


def test_format_datetime():
    t = datetime(2024, 10, 14, 0, 0, 0)
    assert format_datetime(t) == "2024-10-14T00:00:00.000000000Z"

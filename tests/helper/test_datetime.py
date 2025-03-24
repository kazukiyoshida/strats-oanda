from datetime import datetime, timezone

from strats_oanda.helper import format_datetime, parse_time


def test_format_datetime():
    t = datetime(2024, 10, 14, 0, 0, 0)
    assert format_datetime(t) == "2024-10-14T00:00:00.000000000Z"


def test_parse_time():
    s = "2025-03-24T15:34:25.366624289Z"
    assert parse_time(s) == datetime(2025, 3, 24, 15, 34, 25, 366624, tzinfo=timezone.utc)

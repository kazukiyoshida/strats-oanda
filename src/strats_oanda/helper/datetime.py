from datetime import datetime


def format_datetime(t: datetime) -> str:
    """datetime(2024, 10, 14, 0, 0, 0)
    -> "2024-10-14T00:00:00.000000000Z"
    """
    return t.strftime("%Y-%m-%dT%H:%M:%S.%f") + "000Z"


def parse_time(s: str) -> datetime:
    """
    '2025-03-24T15:34:25.366624289Z'
    -> datetime(2025, 3, 24, 15, 34, 25)
    """
    if "." in s:
        datetime_part, frac_part = s.split(".")
        microsec_part = frac_part[:6]
        s = f"{datetime_part}.{microsec_part}Z"
    s = s.replace("Z", "+00:00")
    return datetime.fromisoformat(s)

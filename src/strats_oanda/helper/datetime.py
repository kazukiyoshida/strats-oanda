from datetime import datetime


def format_datetime(t: datetime) -> str:
    """datetime(2024, 10, 14, 0, 0, 0)
    -> "2024-10-14T00:00:00.000000000Z"
    """
    return t.strftime("%Y-%m-%dT%H:%M:%S.%f") + "000Z"

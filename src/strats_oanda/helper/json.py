import json
from decimal import Decimal
from enum import Enum


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Enum):
            return o.value
        if isinstance(o, Decimal):
            return str(o)
        return super().default(o)


def remove_none(obj):
    """
    再帰的に None を含むキー (あるいは要素) を削除して返す。
    """
    if isinstance(obj, dict):
        return {k: remove_none(v) for k, v in obj.items() if v is not None}
    elif isinstance(obj, list):
        return [remove_none(v) for v in obj if v is not None]
    else:
        return obj

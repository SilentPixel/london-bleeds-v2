# JSON utility functions for database JSON columns
import orjson
from typing import Any, Union

def dumps(obj: Any) -> str:
    """Serialize object to JSON string using orjson"""
    return orjson.dumps(obj).decode()

def loads(s: Union[str, None]) -> Any:
    """Deserialize JSON string to object with safe default `{} or []` on None"""
    if s is None:
        return {}
    if not s or not s.strip():
        return {}
    try:
        result = orjson.loads(s)
        # If result is None, return empty dict
        if result is None:
            return {}
        return result
    except:
        # Try to determine if it should be a list or dict by checking first character
        s_stripped = s.strip()
        if s_stripped.startswith('['):
            return []
        return {}



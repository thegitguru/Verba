from __future__ import annotations
import json as _json


def json_parse(s: str) -> dict:
    """Parse a JSON string and return a dict/list accessible via .prop notation."""
    try:
        return _json.loads(s)
    except Exception as e:
        raise RuntimeError(f"json.parse failed: {e}")


def json_get(obj_or_json: str, key: str) -> str:
    """Get a key from a parsed object or raw JSON string."""
    try:
        d = _json.loads(obj_or_json) if isinstance(obj_or_json, str) else obj_or_json
        v = d.get(key) if isinstance(d, dict) else None
        if v is None:
            return ""
        return str(v) if not isinstance(v, str) else v
    except Exception:
        return ""


def json_set(json_str: str, key: str, value: str) -> str:
    """Return a new JSON string with key set to value."""
    try:
        d = _json.loads(json_str) if json_str.strip() else {}
        d[key] = value
        return _json.dumps(d)
    except Exception as e:
        raise RuntimeError(f"json.set failed: {e}")


def json_build(*pairs: str) -> str:
    """Build a JSON object from alternating key, value strings."""
    d = {}
    it = iter(pairs)
    for k in it:
        if not k:  # skip empty trailing slots
            break
        v = next(it, "")
        try:
            v = int(v) if "." not in str(v) else float(v)
        except (ValueError, TypeError):
            pass
        d[k] = v
    return _json.dumps(d)


def json_stringify(value: str) -> str:
    """Wrap a string value as a JSON string (adds quotes, escapes)."""
    return _json.dumps(value)


def json_array_length(json_str: str) -> int:
    try:
        return len(_json.loads(json_str))
    except Exception:
        return 0


def json_array_item(json_str: str, index: str) -> str:
    try:
        arr = _json.loads(json_str)
        item = arr[int(float(index))]
        return item if isinstance(item, str) else _json.dumps(item)
    except Exception:
        return ""


def json_has(json_str: str, key: str) -> str:
    try:
        d = _json.loads(json_str)
        return "true" if key in d else "false"
    except Exception:
        return "false"


def json_keys(json_str: str) -> list:
    try:
        d = _json.loads(json_str)
        return list(d.keys()) if isinstance(d, dict) else []
    except Exception:
        return []


FUNCTIONS: dict[str, tuple] = {
    "parse":      (json_parse,        ["s"]),
    "get":        (json_get,          ["obj", "key"]),
    "set":        (json_set,          ["json", "key", "value"]),
    "build":      (json_build,        ["k1", "v1", "k2", "v2", "k3", "v3", "k4", "v4", "k5", "v5", "k6", "v6"]),
    "stringify":  (json_stringify,    ["value"]),
    "arr_len":    (json_array_length, ["json"]),
    "arr_item":   (json_array_item,   ["json", "index"]),
    "has":        (json_has,          ["json", "key"]),
    "keys":       (json_keys,         ["json"]),
}

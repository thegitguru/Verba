from __future__ import annotations
import os as _os


def env_get(key: str, default: str = "") -> str:
    return _os.environ.get(key, default or "")


def env_set(key: str, value: str) -> str:
    _os.environ[key] = value
    return value


def env_has(key: str) -> str:
    return "true" if key in _os.environ else "false"


def env_all() -> list:
    return [f"{k}={v}" for k, v in _os.environ.items()]


FUNCTIONS: dict[str, tuple] = {
    "get": (env_get, ["key", "default"]),
    "set": (env_set, ["key", "value"]),
    "has": (env_has, ["key"]),
    "all": (env_all, []),
}

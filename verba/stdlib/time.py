from __future__ import annotations
import time as _time
import datetime as _dt


def time_now() -> float:
    return _time.time()


def time_sleep(ms: str) -> str:
    _time.sleep(float(ms) / 1000)
    return "done"


def time_format(timestamp: str = "", fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    try:
        ts = float(timestamp) if timestamp else _time.time()
        return _dt.datetime.fromtimestamp(ts).strftime(fmt or "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        raise RuntimeError(f"time.format failed: {e}")


def time_year() -> int:
    return _dt.datetime.now().year


def time_month() -> int:
    return _dt.datetime.now().month


def time_day() -> int:
    return _dt.datetime.now().day


def time_hour() -> int:
    return _dt.datetime.now().hour


def time_minute() -> int:
    return _dt.datetime.now().minute


def time_second() -> int:
    return _dt.datetime.now().second


def time_since(timestamp: str) -> float:
    return _time.time() - float(timestamp)


FUNCTIONS: dict[str, tuple] = {
    "now":    (time_now,    []),
    "sleep":  (time_sleep,  ["ms"]),
    "format": (time_format, ["timestamp", "fmt"]),
    "year":   (time_year,   []),
    "month":  (time_month,  []),
    "day":    (time_day,    []),
    "hour":   (time_hour,   []),
    "minute": (time_minute, []),
    "second": (time_second, []),
    "since":  (time_since,  ["timestamp"]),
}

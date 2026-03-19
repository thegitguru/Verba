import datetime as _py_dt

def dt_now(format_str=None):
    now = _py_dt.datetime.now()
    if format_str and isinstance(format_str, str):
        return now.strftime(format_str)
    return str(now)

def dt_parse(text, layout):
    if not isinstance(text, str) or not isinstance(layout, str):
        return ""
    try:
        dt = _py_dt.datetime.strptime(text, layout)
        return str(dt)
    except Exception:
        return ""

def dt_format(iso_str, layout):
    if not isinstance(iso_str, str) or not isinstance(layout, str):
        return str(iso_str)
    try:
        dt = _py_dt.datetime.fromisoformat(iso_str)
        return dt.strftime(layout)
    except Exception:
        return str(iso_str)

FUNCTIONS = {
    "now": (dt_now, ["format"]),
    "parse": (dt_parse, ["text", "layout"]),
    "format": (dt_format, ["iso_str", "layout"]),
}

import base64 as _py_b64

def b64_encode(text):
    if not isinstance(text, str):
        text = str(text)
    return _py_b64.b64encode(text.encode("utf-8")).decode("utf-8")

def b64_decode(text):
    if not isinstance(text, str):
        text = str(text)
    try:
        return _py_b64.b64decode(text.encode("utf-8")).decode("utf-8")
    except Exception:
        return ""

FUNCTIONS = {
    "encode": (b64_encode, ["text"]),
    "decode": (b64_decode, ["text"]),
}

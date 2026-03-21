def connect(url):
    try:
        import websockets.sync.client as ws
        conn = ws.connect(str(url))
        return {"_conn": conn, "url": str(url)}
    except Exception as e:
        return {"error": str(e), "url": str(url)}

def send(conn_ni, message):
    conn = conn_ni.props.get("_conn")
    if conn:
        conn.send(str(message))
        return True
    return False

def receive(conn_ni):
    conn = conn_ni.props.get("_conn")
    if conn:
        try:
            return conn.recv()
        except Exception:
            return ""
    return ""

def close(conn_ni):
    conn = conn_ni.props.get("_conn")
    if conn:
        conn.close()
        return True
    return False

# In Verba, we like to return objects with methods.
def vibe_open(url):
    from ..runtime_types import NativeInstance, NativeFunction
    res = connect(url)
    if "error" in res:
        # Error handling? For now just return native instance with error prop.
        ni = NativeInstance("vibe_conn", {})
        ni.props["error"] = res["error"]
        return ni
        
    methods = {}
    methods["send"]    = NativeFunction("send",    ["msg"],    lambda m: send(ni, m))
    methods["receive"] = NativeFunction("receive", [],         lambda: receive(ni))
    methods["close"]   = NativeFunction("close",   [],         lambda: close(ni))
    
    ni = NativeInstance("vibe_conn", methods)
    ni.props["_conn"] = res["_conn"]
    ni.props["url"]   = res["url"]
    return ni

FUNCTIONS = {
    "open": (vibe_open, ["url"]),
}

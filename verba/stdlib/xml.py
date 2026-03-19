import xml.etree.ElementTree as ET

def xml_parse(text):
    try:
        root = ET.fromstring(text)
        return _node_to_dict(root)
    except Exception as e:
        return str(e)

def _node_to_dict(node):
    res = {
        "tag": node.tag,
        "text": node.text.strip() if node.text else "",
        "attributes": node.attrib,
        "children": [_node_to_dict(c) for c in node]
    }
    return res

def xml_find(data, tag):
    # Search in dict representation
    if not isinstance(data, dict):
        return None
    if data.get("tag") == tag:
        return data
    for c in data.get("children", []):
        r = xml_find(c, tag)
        if r: return r
    return None

FUNCTIONS = {
    "parse": (xml_parse, ["text"]),
    "find": (xml_find, ["data", "tag"]),
}

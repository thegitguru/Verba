import re

def regex_match(pattern, text):
    if not isinstance(pattern, str) or not isinstance(text, str):
        return False
    return bool(re.match(pattern, text))

def regex_search(pattern, text):
    if not isinstance(pattern, str) or not isinstance(text, str):
        return False
    return bool(re.search(pattern, text))

def regex_replace(pattern, repl, text):
    if not isinstance(pattern, str) or not isinstance(repl, str) or not isinstance(text, str):
        return str(text)
    return re.sub(pattern, repl, text)

FUNCTIONS = {
    "match": (regex_match, ["pattern", "text"]),
    "search": (regex_search, ["pattern", "text"]),
    "replace": (regex_replace, ["pattern", "replacement", "text"]),
}

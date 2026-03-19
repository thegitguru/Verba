import csv as _py_csv
import os

def csv_read(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8', newline='') as f:
            reader = _py_csv.DictReader(f)
            return [dict(row) for row in reader]
    except Exception:
        return []

def csv_write(path, data):
    if not isinstance(data, list) or not data:
        return False
    try:
        keys = data[0].keys()
        with open(path, 'w', encoding='utf-8', newline='') as f:
            writer = _py_csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
        return True
    except Exception:
        return False

FUNCTIONS = {
    "read": (csv_read, ["path"]),
    "write": (csv_write, ["path", "data"]),
}

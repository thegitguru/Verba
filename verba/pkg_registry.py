"""Local package registry — tracks installed Verba packages."""
from __future__ import annotations

import json
from pathlib import Path

MODULES_DIR = Path("modules")
REGISTRY_FILE = MODULES_DIR / ".registry.json"


def _load() -> dict:
    if REGISTRY_FILE.exists():
        try:
            return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save(data: dict) -> None:
    MODULES_DIR.mkdir(exist_ok=True)
    REGISTRY_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def record_install(name: str, url: str, version: str = "unknown") -> None:
    data = _load()
    data[name] = {"url": url, "version": version}
    _save(data)


def record_uninstall(name: str) -> bool:
    data = _load()
    if name not in data:
        return False
    del data[name]
    _save(data)
    return True


def list_packages() -> dict:
    return _load()


def get_package(name: str) -> dict | None:
    return _load().get(name)

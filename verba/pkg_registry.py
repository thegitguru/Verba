"""pkg_registry.py — Local registry and lock file management for Verbix."""
from __future__ import annotations

import json
from pathlib import Path

MODULES_DIR = Path("modules")
REGISTRY_FILE = MODULES_DIR / ".registry.json"
LOCK_FILE = Path("verba.lock")


# ── Internal helpers ──────────────────────────────────────────────────────────

def _load_registry() -> dict:
    if REGISTRY_FILE.exists():
        try:
            return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_registry(data: dict) -> None:
    MODULES_DIR.mkdir(exist_ok=True)
    REGISTRY_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _load_lock() -> dict:
    if LOCK_FILE.exists():
        try:
            return json.loads(LOCK_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_lock(data: dict) -> None:
    LOCK_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


# ── Public API ────────────────────────────────────────────────────────────────

def record_install(name: str, url: str, version: str = "unknown") -> None:
    """Record a package install in .registry.json and verba.lock."""
    data = _load_registry()
    data[name] = {"url": url, "version": version}
    _save_registry(data)

    lock = _load_lock()
    lock[name] = version
    _save_lock(lock)


def record_uninstall(name: str) -> bool:
    """Remove a package from .registry.json and verba.lock. Returns True if found."""
    data = _load_registry()
    found = name in data
    if found:
        del data[name]
        _save_registry(data)

    lock = _load_lock()
    if name in lock:
        del lock[name]
        _save_lock(lock)

    return found


def list_packages() -> dict:
    """Return all installed packages as {name: {url, version}}."""
    return _load_registry()


def get_package(name: str) -> dict | None:
    """Return install info for a package, or None if not installed."""
    return _load_registry().get(name)


def is_installed(name: str, version: str | None = None) -> bool:
    """Return True if package is installed (optionally at a specific version)."""
    pkg = get_package(name)
    if pkg is None:
        return False
    if version is not None:
        return pkg.get("version") == version
    return True


def get_lock() -> dict:
    """Return the full lock file contents."""
    return _load_lock()


def sync_lock() -> None:
    """Rebuild verba.lock from .registry.json (backfills missing lock file)."""
    data = _load_registry()
    lock = {name: info.get("version", "unknown") for name, info in data.items()}
    _save_lock(lock)

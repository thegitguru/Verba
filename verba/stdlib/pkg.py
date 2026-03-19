"""verbix — Verbix package manager stdlib module for Verba.

Available in every script as `verbix`:
    verbix.install with url
    verbix.uninstall with name
    verbix.list
    verbix.info with name
    verbix.installed with name   -> "true" / "false"
"""
from __future__ import annotations

import urllib.request
from pathlib import Path

from verba.pkg_registry import (
    record_install,
    record_uninstall,
    list_packages,
    get_package,
    MODULES_DIR,
)


def _install(url: str) -> str:
    from urllib.parse import urlparse
    name = Path(urlparse(url).path).name
    if not name:
        raise RuntimeError(f"Cannot determine package name from URL: {url}")
    if not name.endswith(".vrb"):
        name += ".vrb"
    MODULES_DIR.mkdir(exist_ok=True)
    with urllib.request.urlopen(url) as r:
        content = r.read()
    (MODULES_DIR / name).write_bytes(content)
    record_install(name, url)
    return f"Installed {name}"


def _uninstall(name: str) -> str:
    if not name.endswith(".vrb"):
        name += ".vrb"
    path = MODULES_DIR / name
    removed_file = False
    if path.exists():
        path.unlink()
        removed_file = True
    removed_reg = record_uninstall(name)
    if removed_file or removed_reg:
        return f"Uninstalled {name}"
    return f"Package {name} was not installed"


def _list() -> str:
    pkgs = list_packages()
    if not pkgs:
        return "No packages installed."
    lines = [f"{n}  ({v['version']})  {v['url']}" for n, v in pkgs.items()]
    return "\n".join(lines)


def _info(name: str) -> str:
    if not name.endswith(".vrb"):
        name += ".vrb"
    pkg = get_package(name)
    if pkg is None:
        return f"Package {name} is not installed."
    return f"name: {name}\nversion: {pkg['version']}\nurl: {pkg['url']}"


def _installed(name: str) -> str:
    if not name.endswith(".vrb"):
        name += ".vrb"
    return "true" if get_package(name) is not None else "false"


FUNCTIONS: dict = {
    "install":   (_install,   ["url"]),
    "uninstall": (_uninstall, ["name"]),
    "list":      (_list,      []),
    "info":      (_info,      ["name"]),
    "installed": (_installed, ["name"]),
}

NEEDS_INTERP: set = set()

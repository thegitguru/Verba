"""verbix — Verbix package manager stdlib module for Verba scripts.

Available in every script as `verbix`:
    verbix.install with name_or_url
    verbix.uninstall with name
    verbix.list
    verbix.info with name
    verbix.installed with name
    verbix.search with query
"""
from __future__ import annotations

from verba.pkg_registry import (
    list_packages,
    get_package,
    is_installed,
    MODULES_DIR,
)


def _install(name_or_url: str) -> str:
    from verba.verbix_cli import install_cmd
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = install_cmd(name_or_url)
    out = buf.getvalue().strip()
    return out if out else ("OK" if code == 0 else "Install failed.")


def _uninstall(name: str) -> str:
    from verba.verbix_cli import uninstall_cmd
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        uninstall_cmd(name)
    return buf.getvalue().strip()


def _list() -> str:
    pkgs = list_packages()
    if not pkgs:
        return "No packages installed."
    lines = [f"{n}  v{v.get('version','?')}" for n, v in pkgs.items()]
    return "\n".join(lines)


def _info(name: str) -> str:
    from verba.verbix_cli import info_cmd
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        info_cmd(name)
    return buf.getvalue().strip()


def _installed(name: str) -> str:
    return "true" if is_installed(name.lower()) else "false"


def _search(query: str) -> str:
    from verba.verbix_cli import search_cmd
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        search_cmd(query)
    return buf.getvalue().strip()


FUNCTIONS: dict = {
    "install":   (_install,   ["name_or_url"]),
    "uninstall": (_uninstall, ["name"]),
    "list":      (_list,      []),
    "info":      (_info,      ["name"]),
    "installed": (_installed, ["name"]),
    "search":    (_search,    ["query"]),
}

NEEDS_INTERP: set = set()

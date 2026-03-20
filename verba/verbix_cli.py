"""verbix_cli.py — Verbix package manager for the Verba programming language."""
from __future__ import annotations

import argparse
import io
import json
import shutil
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from urllib.parse import urlparse

# ── Config ────────────────────────────────────────────────────────────────────

_CONFIG_FILE = Path(__file__).parent.parent / "verbix.config.json"
_DEFAULT_REGISTRY = "http://localhost:8900/index.json"
_VERBIX_VERSION = "2.0.0"


def _registry_url() -> str:
    if _CONFIG_FILE.exists():
        try:
            return json.loads(
                _CONFIG_FILE.read_text(encoding="utf-8")
            ).get("registry", _DEFAULT_REGISTRY)
        except Exception:
            pass
    return _DEFAULT_REGISTRY


# ── Core install functions ────────────────────────────────────────────────────

def fetch_registry() -> dict:
    """
    Fetch the remote package registry JSON.

    Expected format:
        {
            "packages": {
                "mathkit": {
                    "latest": "1.2.0",
                    "description": "...",
                    "versions": {
                        "1.0.0": {"url": "https://.../mathkit-1.0.0.zip"},
                        "1.2.0": {"url": "https://.../mathkit-1.2.0.zip"}
                    }
                }
            }
        }

    Raises RuntimeError on network or parse failure.
    """
    url = _registry_url()
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error fetching registry from {url}: {e}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Registry at {url} returned invalid JSON: {e}")

    if "packages" not in raw:
        raise RuntimeError(
            f"Registry at {url} is missing the top-level 'packages' key."
        )
    return raw["packages"]


def resolve_version(index: dict, name: str, requested: str | None) -> str:
    """
    Resolve which version to install for a package.

    - If requested is None or 'latest' → use index[name]['latest']
    - Otherwise validate the requested version exists.

    Raises RuntimeError if the package or version is not found.
    """
    key = name.lower()
    if key not in index:
        available = ", ".join(sorted(index.keys()))
        raise RuntimeError(
            f"Package '{name}' not found in registry.\n"
            f"Available packages: {available}"
        )

    entry = index[key]
    versions: dict = entry.get("versions", {})

    if not versions:
        raise RuntimeError(f"Package '{name}' has no versions in the registry.")

    if requested is None or requested == "latest":
        ver = entry.get("latest") or max(
            versions.keys(),
            key=lambda v: tuple(int(x) for x in v.split(".") if x.isdigit()),
        )
    else:
        ver = requested

    if ver not in versions:
        available_vers = ", ".join(sorted(versions.keys()))
        raise RuntimeError(
            f"Version '{ver}' not found for '{name}'.\n"
            f"Available versions: {available_vers}"
        )

    return ver


def download_package(url: str, name: str, version: str) -> bytes:
    """
    Download a package from the given URL.

    Returns raw bytes of the file (ZIP or .vrb).
    Raises RuntimeError on network failure.
    """
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = resp.read()
    except urllib.error.URLError as e:
        raise RuntimeError(
            f"Failed to download {name}@{version} from {url}: {e}"
        )

    if not data:
        raise RuntimeError(
            f"Downloaded empty file for {name}@{version} from {url}."
        )

    return data


def extract_package(data: bytes, name: str, url: str = "") -> Path:
    """
    Save a package into modules/<name>/.

    - If the data is a ZIP archive → extract it
    - If the data is a .vrb file → save as modules/<name>/<name>.vrb

    Returns the path to the package directory.
    """
    from verba.pkg_registry import MODULES_DIR

    dest = MODULES_DIR / name
    dest.mkdir(parents=True, exist_ok=True)

    # Detect ZIP by magic bytes (PK\x03\x04)
    is_zip = data[:4] == b"PK\x03\x04"

    if is_zip:
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                members = zf.namelist()
                top_dirs = {m.split("/")[0] for m in members if "/" in m}
                all_under_one = (
                    len(top_dirs) == 1
                    and all(m.startswith(next(iter(top_dirs))) for m in members)
                )
                strip_prefix = (next(iter(top_dirs)) + "/") if all_under_one else ""

                for member in members:
                    rel = member[len(strip_prefix):] if strip_prefix else member
                    if not rel:
                        continue
                    target = dest / rel
                    if member.endswith("/"):
                        target.mkdir(parents=True, exist_ok=True)
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(zf.read(member))
        except zipfile.BadZipFile as e:
            shutil.rmtree(dest, ignore_errors=True)
            raise RuntimeError(
                f"Downloaded file for '{name}' is not a valid ZIP archive: {e}"
            )
    else:
        # Plain .vrb file — save directly
        vrb_file = dest / f"{name}.vrb"
        vrb_file.write_bytes(data)

    return dest


def _read_verba_json(pkg_dir: Path, name: str) -> dict:
    """
    Read and validate verba.json from an extracted package directory.

    Returns the parsed dict. Raises RuntimeError on missing/invalid file.
    """
    vj = pkg_dir / "verba.json"
    if not vj.exists():
        # Non-fatal: package may be a single-file legacy package
        return {"name": name, "version": "unknown", "main": f"{name}.vrb", "dependencies": {}}

    try:
        data = json.loads(vj.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid verba.json in package '{name}': {e}")

    if not isinstance(data, dict):
        raise RuntimeError(f"verba.json in '{name}' must be a JSON object.")

    return data


def install_dependencies(
    deps: dict,
    index: dict,
    *,
    installed: set[str],
    visiting: set[str],
    depth: int = 0,
) -> None:
    """
    Recursively install dependencies declared in verba.json.

    - deps: {package_name: version_constraint}
    - installed: set of already-installed package names (mutated in place)
    - visiting: set of packages currently being resolved (cycle detection)
    - depth: current recursion depth (for indented log output)
    """
    indent = "  " * depth
    for dep_name, dep_ver_req in deps.items():
        key = dep_name.lower()

        if key in visiting:
            print(f"{indent}  [warn] Circular dependency detected for '{dep_name}', skipping.")
            continue

        # Resolve the exact version
        try:
            ver = resolve_version(index, key, dep_ver_req if dep_ver_req != "*" else None)
        except RuntimeError as e:
            raise RuntimeError(f"Dependency '{dep_name}': {e}")

        if key in installed:
            from verba.pkg_registry import get_package
            existing = get_package(key)
            if existing and existing.get("version") == ver:
                print(f"{indent}  [skip] {dep_name}@{ver} already installed.")
                continue

        install_package(
            key,
            requested_version=ver,
            index=index,
            installed=installed,
            visiting=visiting,
            depth=depth + 1,
        )


def install_package(
    name: str,
    *,
    requested_version: str | None = None,
    index: dict | None = None,
    installed: set[str] | None = None,
    visiting: set[str] | None = None,
    depth: int = 0,
) -> int:
    """
    Full install pipeline for a single package:
      1. Resolve version
      2. Check if already installed
      3. Download ZIP
      4. Extract to modules/<name>/
      5. Read verba.json
      6. Record in registry + lock file
      7. Recursively install dependencies

    Returns 0 on success, 1 on failure.
    """
    from verba.pkg_registry import record_install, is_installed, MODULES_DIR

    indent = "  " * depth

    # Lazy-load registry if not provided (top-level call)
    if index is None:
        try:
            index = fetch_registry()
        except RuntimeError as e:
            print(f"{indent}[error] {e}")
            return 1

    if installed is None:
        installed = set()
    if visiting is None:
        visiting = set()

    key = name.lower()

    # Resolve version
    try:
        version = resolve_version(index, key, requested_version)
    except RuntimeError as e:
        print(f"{indent}[error] {e}")
        return 1

    # Skip if already installed at this version
    if is_installed(key, version):
        print(f"{indent}[skip] {key}@{version} is already installed.")
        installed.add(key)
        return 0

    # Mark as being visited (cycle guard)
    visiting.add(key)

    url = index[key]["versions"][version]["url"]
    print(f"{indent}Installing {key}@{version}...")

    # Download
    try:
        data = download_package(url, key, version)
    except RuntimeError as e:
        print(f"{indent}[error] {e}")
        visiting.discard(key)
        return 1

    # Extract
    try:
        pkg_dir = extract_package(data, key, url)
    except RuntimeError as e:
        print(f"{indent}[error] {e}")
        visiting.discard(key)
        return 1

    # Read verba.json
    try:
        meta = _read_verba_json(pkg_dir, key)
    except RuntimeError as e:
        print(f"{indent}[error] {e}")
        visiting.discard(key)
        return 1

    # Record install
    record_install(key, url, version)
    installed.add(key)
    visiting.discard(key)

    print(f"{indent}  Installed {key}@{version} -> {pkg_dir}")

    # Install dependencies
    deps: dict = meta.get("dependencies") or {}
    if deps:
        try:
            install_dependencies(
                deps,
                index,
                installed=installed,
                visiting=visiting,
                depth=depth,
            )
        except RuntimeError as e:
            print(f"{indent}[error] Dependency error: {e}")
            return 1

    return 0


# ── Other commands ────────────────────────────────────────────────────────────

def _parse_name_version(arg: str) -> tuple[str, str | None]:
    """Split 'mathkit@1.0.0' -> ('mathkit', '1.0.0'), 'mathkit' -> ('mathkit', None)."""
    if "@" in arg:
        name, _, ver = arg.partition("@")
        return name.strip().lower(), ver.strip()
    return arg.strip().lower(), None


def _semver_gt(a: str, b: str) -> bool:
    """Return True if version string a is greater than b."""
    try:
        return tuple(int(x) for x in a.split(".")) > tuple(int(x) for x in b.split("."))
    except Exception:
        return a != b


def install_cmd(name_or_url: str) -> int:
    """Entry point for `verbix install <name[@version] | url>`."""
    # Direct URL install (no registry lookup, no verba.json deps)
    if name_or_url.startswith("http://") or name_or_url.startswith("https://"):
        return _install_from_url(name_or_url)

    name, ver = _parse_name_version(name_or_url)
    return install_package(name, requested_version=ver)


def _install_from_url(url: str) -> int:
    """Install a package directly from a URL (bypasses registry)."""
    from verba.pkg_registry import record_install

    pkg_name = Path(urlparse(url).path).stem.lower()
    print(f"Installing {pkg_name} from {url}...")
    try:
        data = download_package(url, pkg_name, "unknown")
        pkg_dir = extract_package(data, pkg_name, url)
        meta = _read_verba_json(pkg_dir, pkg_name)
        version = meta.get("version", "unknown")
        record_install(pkg_name, url, version)
        print(f"  Installed {pkg_name}@{version} -> {pkg_dir}")
        return 0
    except RuntimeError as e:
        print(f"[error] {e}")
        return 1


def uninstall_cmd(name: str) -> int:
    from verba.pkg_registry import record_uninstall, MODULES_DIR

    key = name.lower()
    pkg_dir = MODULES_DIR / key
    removed_dir = False
    if pkg_dir.exists():
        shutil.rmtree(pkg_dir)
        removed_dir = True

    removed_reg = record_uninstall(key)
    if removed_dir or removed_reg:
        print(f"Verbix: uninstalled '{key}'.")
        return 0
    print(f"Verbix: package '{key}' is not installed.")
    return 1


def upgrade_cmd(name: str) -> int:
    from verba.pkg_registry import get_package

    key = name.lower()
    existing = get_package(key)
    try:
        index = fetch_registry()
    except RuntimeError as e:
        print(f"[error] {e}")
        return 1

    if key not in index:
        print(f"Verbix: '{key}' not found in registry.")
        return 1

    latest = index[key].get("latest") or ""
    if existing and not _semver_gt(latest, existing.get("version", "0.0.0")):
        print(f"Verbix: '{key}' is already at latest version ({latest}).")
        return 0

    old = existing.get("version", "none") if existing else "none"
    print(f"Verbix: upgrading '{key}' {old} -> {latest}...")
    return install_package(key, requested_version=latest, index=index)


def upgrade_all_cmd() -> int:
    from verba.pkg_registry import list_packages

    pkgs = list_packages()
    if not pkgs:
        print("Verbix: no packages installed.")
        return 0
    code = 0
    for pkg_name in pkgs:
        code |= upgrade_cmd(pkg_name)
    return code


def outdated_cmd() -> int:
    from verba.pkg_registry import list_packages

    pkgs = list_packages()
    if not pkgs:
        print("Verbix: no packages installed.")
        return 0
    try:
        index = fetch_registry()
    except RuntimeError as e:
        print(f"[error] {e}")
        return 1

    print(f"{'Package':<25} {'Installed':<12} {'Latest':<12} Status")
    print("-" * 65)

    outdated: list[tuple[str, str, str]] = []  # (name, installed_ver, latest_ver)
    for pkg_name, info in pkgs.items():
        installed_ver = info.get("version", "unknown")
        if pkg_name in index:
            latest = index[pkg_name].get("latest", "?")
            if _semver_gt(latest, installed_ver):
                status = "OUTDATED"
                outdated.append((pkg_name, installed_ver, latest))
            else:
                status = "up to date"
        else:
            latest = "?"
            status = "not in registry"
        print(f"{pkg_name:<25} {installed_ver:<12} {latest:<12} {status}")

    if not outdated:
        print("\nAll packages are up to date.")
        return 0

    print(f"\n{len(outdated)} package(s) can be updated.")

    # Ask per-package or upgrade all at once
    try:
        answer = input("Upgrade all outdated packages? [y/n/ask]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return 0

    if answer in ("y", "yes"):
        to_upgrade = outdated
    elif answer in ("ask", "a"):
        to_upgrade = []
        for name, old, new in outdated:
            try:
                ans = input(f"  Upgrade {name} {old} -> {new}? [y/n]: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if ans in ("y", "yes"):
                to_upgrade.append((name, old, new))
    else:
        print("Skipped. Run 'verbix upgrade <name>' to upgrade individually.")
        return 0

    if not to_upgrade:
        print("Nothing to upgrade.")
        return 0

    print()
    code = 0
    for name, old, new in to_upgrade:
        print(f"Upgrading {name} {old} -> {new}...")
        code |= install_package(name, requested_version=new, index=index)

    print("\nDone.")
    return code


def list_cmd() -> int:
    from verba.pkg_registry import list_packages

    pkgs = list_packages()
    if not pkgs:
        print("Verbix: no packages installed.")
        return 0
    print(f"{'Package':<25} {'Version':<12} Location")
    print("-" * 65)
    from verba.pkg_registry import MODULES_DIR
    for pkg_name, info in pkgs.items():
        loc = MODULES_DIR / pkg_name
        print(f"{pkg_name:<25} {info.get('version','?'):<12} {loc}")
    return 0


def info_cmd(name: str) -> int:
    from verba.pkg_registry import get_package, MODULES_DIR

    key = name.lower()
    pkg = get_package(key)

    try:
        index = fetch_registry()
        reg_entry = index.get(key, {})
        available_versions = sorted(reg_entry.get("versions", {}).keys())
        latest = reg_entry.get("latest", "?")
    except RuntimeError:
        available_versions = []
        latest = "?"

    if pkg is None:
        print(f"Verbix: package '{key}' is not installed.")
        if available_versions:
            print(f"Available versions: {', '.join(available_versions)}")
            print(f"Install with: verbix install {key}")
        return 1

    installed_ver = pkg.get("version", "?")
    outdated = _semver_gt(latest, installed_ver) if latest != "?" else False
    pkg_dir = MODULES_DIR / key

    print(f"Name:      {key}")
    print(f"Installed: {installed_ver}")
    print(f"Latest:    {latest}{' (upgrade available)' if outdated else ''}")
    print(f"URL:       {pkg.get('url', '?')}")
    print(f"Path:      {pkg_dir} ({'exists' if pkg_dir.exists() else 'missing'})")
    if available_versions:
        print(f"Versions:  {', '.join(available_versions)}")

    # Show verba.json metadata if present
    vj = pkg_dir / "verba.json"
    if vj.exists():
        try:
            meta = json.loads(vj.read_text(encoding="utf-8"))
            if meta.get("description"):
                print(f"Desc:      {meta['description']}")
            if meta.get("dependencies"):
                deps = ", ".join(
                    f"{k}@{v}" for k, v in meta["dependencies"].items()
                )
                print(f"Deps:      {deps}")
        except Exception:
            pass

    return 0


def search_cmd(query: str) -> int:
    try:
        index = fetch_registry()
    except RuntimeError as e:
        print(f"[error] {e}")
        return 1

    q = query.lower()
    results = {
        k: v for k, v in index.items()
        if q in k.lower() or q in v.get("description", "").lower()
    }
    if not results:
        print(f"Verbix: no packages found matching '{query}'.")
        return 0

    from verba.pkg_registry import get_package
    for k, v in results.items():
        installed = get_package(k)
        installed_ver = f" (installed: {installed['version']})" if installed else ""
        versions = list(v.get("versions", {}).keys())
        latest = v.get('latest', '?')
        print(f"  {k} — {v.get('description', 'no description')}{installed_ver}")
        print(f"    Latest   : {latest}")
        print(f"    Versions : {', '.join(versions)}")
        print(f"    Author   : {v.get('author', '?')}")
        print(f"    License  : {v.get('license', '?')}")
        print()
    return 0


def lock_cmd() -> int:
    """Display the current verba.lock file."""
    from verba.pkg_registry import get_lock, sync_lock

    sync_lock()  # always backfill from registry before displaying
    lock = get_lock()
    if not lock:
        print("Verbix: no packages installed — verba.lock is empty.")
        return 0
    print(f"{'Package':<25} Version")
    print("-" * 40)
    for pkg, ver in sorted(lock.items()):
        print(f"{pkg:<25} {ver}")
    return 0


def sync_cmd() -> int:
    """Rebuild verba.lock from .registry.json."""
    from verba.pkg_registry import sync_lock, get_lock

    sync_lock()
    lock = get_lock()
    if not lock:
        print("Verbix: nothing to sync — no packages installed.")
        return 0
    print("verba.lock synced:")
    for pkg, ver in sorted(lock.items()):
        print(f"  {pkg} = {ver}")
    return 0


# ── CLI entry point ───────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    raw = argv if argv is not None else sys.argv[1:]

    if not raw:
        print("Verbix — Verba Package Manager")
        print("  verbix install <name[@ver]|url>  Install a package")
        print("  verbix uninstall <name>           Uninstall a package")
        print("  verbix upgrade <name|all>         Upgrade package(s)")
        print("  verbix outdated                   Show outdated packages")
        print("  verbix packages                   List installed packages")
        print("  verbix search <query>             Search the registry")
        print("  verbix info <name>                Show package info")
        print("  verbix lock                       Show verba.lock")
        print("  verbix sync                       Rebuild verba.lock from installed packages")
        print("  verbix --version                  Show Verbix version")
        return 0

    if raw == ["--version"]:
        print(f"verbix {_VERBIX_VERSION}")
        return 0

    p = argparse.ArgumentParser(prog="verbix", description="Verbix — Verba Package Manager")
    sub = p.add_subparsers(dest="command")

    inst_p = sub.add_parser("install", help="Install a package by name[@version] or URL.")
    inst_p.add_argument("name_or_url")

    uninst_p = sub.add_parser("uninstall", help="Uninstall a package.")
    uninst_p.add_argument("name")

    upg_p = sub.add_parser("upgrade", help="Upgrade a package (or 'all').")
    upg_p.add_argument("name")

    sub.add_parser("outdated", help="Show packages with newer versions available.")
    sub.add_parser("packages", help="List installed packages.")
    sub.add_parser("lock", help="Show verba.lock contents.")
    sub.add_parser("sync", help="Rebuild verba.lock from installed packages.")

    info_p = sub.add_parser("info", help="Show package info and available versions.")
    info_p.add_argument("name")

    search_p = sub.add_parser("search", help="Search the registry.")
    search_p.add_argument("query")

    ns = p.parse_args(raw)

    if ns.command == "install":   return install_cmd(ns.name_or_url)
    if ns.command == "uninstall": return uninstall_cmd(ns.name)
    if ns.command == "upgrade":
        return upgrade_all_cmd() if ns.name == "all" else upgrade_cmd(ns.name)
    if ns.command == "outdated":  return outdated_cmd()
    if ns.command == "packages":  return list_cmd()
    if ns.command == "info":      return info_cmd(ns.name)
    if ns.command == "search":    return search_cmd(ns.query)
    if ns.command == "lock":      return lock_cmd()
    if ns.command == "sync":      return sync_cmd()

    p.print_help()
    return 0

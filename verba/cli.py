from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .errors import VerbaError, VerbaParseError, VerbaRuntimeError
from .parser import parse
from .runtime import Interpreter


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


def run_file(path: Path) -> int:
    source = _read_text(path)
    program = parse(source)
    Interpreter().run(program)
    return 0


def check_file(path: Path) -> int:
    source = _read_text(path)
    parse(source)
    print(f"OK: {path}")
    return 0


def repl() -> int:
    print("Verba REPL. Type 'end.' on its own line to exit.")
    try:
        import readline  # noqa: F401 — enables arrow-key history on Unix/Windows
    except ImportError:
        pass
    interp = Interpreter()
    buf: list[str] = []
    while True:
        try:
            line = input("verba ")
        except EOFError:
            print()
            break
        if line.strip().lower() == "end.":
            break
        buf.append(line)
        # Try to parse the whole buffer so blocks can be typed across multiple lines.
        try:
            program = parse("\n".join(buf))
        except VerbaParseError as e:
            # Keep buffering only if it's an unfinished block.
            if str(e).startswith("I expected 'end"):
                continue
            print(e, file=sys.stderr)
            buf = []
            continue
        try:
            interp.run(program)
        except VerbaError as e:
            print(e, file=sys.stderr)
        buf = []
    return 0



def _verbix_main(args: list[str]) -> int:
    """Delegate 'verba verbix ...' to the full verbix_cli."""
    from verba.verbix_cli import main as verbix_main
    return verbix_main(args)


def format_file(path: Path) -> int:
    try:
        source = path.read_text(encoding="utf-8")
        lines = source.splitlines()
        indent = 0
        new_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                new_lines.append("")
                continue
            
            ls = stripped.lower()
            # words that decrease indent for the current line
            if ls.startswith("end.") or ls.startswith("else:") or ls.startswith("otherwise:") or ls.startswith("on error") or ls.startswith("finally:"):
                indent = max(0, indent - 4)
            
            new_lines.append(" " * indent + stripped)
            
            # words that increase indent for the NEXT lines
            if stripped.endswith(":") or ls.endswith("as follows:"):
                indent += 4
        
        path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        print(f"Formatted {path}")
        return 0
    except Exception as e:
        print(f"I failed to format the file: {e}")
        return 1


def main(argv: list[str] | None = None) -> int:
    raw = argv if argv is not None else sys.argv[1:]

    # Legacy flag handling (before argparse sees subcommands)
    if not raw:
        return repl()
    if raw == ["--version"]:
        print("verba 0.1.0")
        return 0
    if raw == ["--repl"]:
        return repl()
    if len(raw) == 2 and raw[0] == "--check":
        try:
            return check_file(Path(raw[1]))
        except (VerbaParseError, VerbaRuntimeError) as e:
            print(e, file=sys.stderr)
            return 1
    if len(raw) == 1 and raw[0].endswith(".vrb"):
        try:
            return run_file(Path(raw[0]))
        except (VerbaParseError, VerbaRuntimeError) as e:
            print(e, file=sys.stderr)
            return 1

    # "verba verbix <cmd> [args]" — Verbix package manager namespace
    if raw and raw[0] == "verbix":
        return _verbix_main(raw[1:])

    p = argparse.ArgumentParser(prog="verba", description="Run Verba programs.")
    sub = p.add_subparsers(dest="command")

    run_p = sub.add_parser("run", help="Run a Verba script.")
    run_p.add_argument("file")

    check_p = sub.add_parser("check", help="Parse without running.")
    check_p.add_argument("file")

    sub.add_parser("repl", help="Start interactive shell.")

    inst_p = sub.add_parser("install", help="Install a package from a URL.")
    inst_p.add_argument("url")

    uninst_p = sub.add_parser("uninstall", help="Uninstall a package by name.")
    uninst_p.add_argument("name")

    sub.add_parser("packages", help="List installed packages.")

    info_p = sub.add_parser("pkg-info", help="Show info about an installed package.")
    info_p.add_argument("name")

    fmt_p = sub.add_parser("format", help="Format a Verba script.")
    fmt_p.add_argument("file")

    ns = p.parse_args(raw)

    try:
        if ns.command == "run":       return run_file(Path(ns.file))
        if ns.command == "check":     return check_file(Path(ns.file))
        if ns.command == "repl":      return repl()
        if ns.command == "install":   return install_pkg(ns.url)
        if ns.command == "uninstall": return uninstall_pkg(ns.name)
        if ns.command == "packages":  return list_pkgs()
        if ns.command == "pkg-info":  return pkg_info(ns.name)
        if ns.command == "format":    return format_file(Path(ns.file))
        return repl()
    except (VerbaParseError, VerbaRuntimeError) as e:
        print(e, file=sys.stderr)
        return 1
    except VerbaError as e:
        print(e, file=sys.stderr)
        return 1

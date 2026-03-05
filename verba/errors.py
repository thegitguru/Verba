from __future__ import annotations


class VerbaError(Exception):
    pass


class VerbaParseError(VerbaError):
    def __init__(self, message: str, *, line_no: int | None = None, line: str | None = None):
        parts: list[str] = []
        if line_no is not None:
            parts.append(f"line {line_no}")
        if line is not None and line.strip():
            parts.append(f"'{line.strip()}'")
        where = ""
        if parts:
            where = " (" + ", ".join(parts) + ")"
        super().__init__(message + where)


class VerbaRuntimeError(VerbaError):
    def __init__(self, message: str, *, line_no: int | None = None):
        if line_no is not None:
            message = f"{message} (line {line_no})"
        super().__init__(message)

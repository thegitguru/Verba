from __future__ import annotations
import os as _os
import shutil


def os_exists(path: str) -> str:
    return "true" if _os.path.exists(path) else "false"


def os_is_file(path: str) -> str:
    return "true" if _os.path.isfile(path) else "false"


def os_is_dir(path: str) -> str:
    return "true" if _os.path.isdir(path) else "false"


def os_list(path: str = ".") -> list:
    try:
        return _os.listdir(path or ".")
    except Exception as e:
        raise RuntimeError(f"os.list failed: {e}")


def os_mkdir(path: str) -> str:
    try:
        _os.makedirs(path, exist_ok=True)
        return path
    except Exception as e:
        raise RuntimeError(f"os.mkdir failed: {e}")


def os_remove(path: str) -> str:
    try:
        if _os.path.isdir(path):
            shutil.rmtree(path)
        else:
            _os.remove(path)
        return "removed"
    except Exception as e:
        raise RuntimeError(f"os.remove failed: {e}")


def os_rename(src: str, dst: str) -> str:
    try:
        _os.rename(src, dst)
        return dst
    except Exception as e:
        raise RuntimeError(f"os.rename failed: {e}")


def os_cwd() -> str:
    return _os.getcwd()


def os_join(a: str, b: str) -> str:
    return _os.path.join(a, b)


def os_basename(path: str) -> str:
    return _os.path.basename(path)


def os_dirname(path: str) -> str:
    return _os.path.dirname(path)


def os_size(path: str) -> int:
    try:
        return _os.path.getsize(path)
    except Exception as e:
        raise RuntimeError(f"os.size failed: {e}")


FUNCTIONS: dict[str, tuple] = {
    "exists":   (os_exists,   ["path"]),
    "is_file":  (os_is_file,  ["path"]),
    "is_dir":   (os_is_dir,   ["path"]),
    "list":     (os_list,     ["path"]),
    "mkdir":    (os_mkdir,    ["path"]),
    "remove":   (os_remove,   ["path"]),
    "rename":   (os_rename,   ["src", "dst"]),
    "cwd":      (os_cwd,      []),
    "join":     (os_join,     ["a", "b"]),
    "basename": (os_basename, ["path"]),
    "dirname":  (os_dirname,  ["path"]),
    "size":     (os_size,     ["path"]),
}

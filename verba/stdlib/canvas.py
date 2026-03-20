from __future__ import annotations
"""
canvas — 2D drawing module for Verba.
Backed by tkinter.Canvas. No third-party dependencies.

Usage in Verba:
    c = the result of running canvas.new with "My Drawing", 800, 600.
    run c.background with "#1e1e2e".
    run c.circle with 400, 300, 80, fill = "#cba6f7".
    run c.rect with 50, 50, 200, 100, fill = "#a6e3a1", outline = "#40a02b".
    run c.line with 0, 0, 800, 600, color = "#f38ba8", width = 3.
    run c.text with 100, 100, "Hello Verba!", color = "#cdd6f4", size = 24.
    run c.polygon with "100,50,200,200,0,200", fill = "#89dceb".
    run c.image with 50, 50, "logo.png".
    run c.on_click with "handle_click".    /- callback receives x, y as globals
    run c.on_key with "handle_key".        /- callback receives key as global
    run c.clear.
    run c.save with "output.ps".           /- save as PostScript
    run c.show.                            /- open window (blocking)
    run c.update.                          /- refresh without blocking
    run c.close.
"""

import tkinter as tk
from tkinter import font as tkfont
from typing import Any


def _f(v: Any, default: float = 0.0) -> float:
    """Safely convert a Verba value to float.

    The Verba runtime passes "" (empty string) for any NativeFunction
    parameter that was not supplied by the caller (optional params).
    This helper treats "" — and any other non-numeric value — as `default`
    rather than raising ValueError.
    """
    if v == "" or v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


class _VerbaCanvas:
    """Wraps a tkinter Tk + Canvas for Verba scripts."""

    def __init__(self, title: str, width: int, height: int, interp: Any):
        self.interp = interp
        self.width = width
        self.height = height
        self._items: list[int] = []
        try:
            self.root = tk.Tk()
            self.root.title(title)
            self.root.resizable(False, False)
            self.cv = tk.Canvas(
                self.root,
                width=width,
                height=height,
                bg="#000000",
                highlightthickness=0,
            )
            self.cv.pack()
        except Exception as e:
            print(f"[canvas] Could not create window: {e}")
            self.root = None
            self.cv = None

    # ── drawing primitives ────────────────────────────────────────────────────

    def background(self, color: str = "#000000") -> str:
        if self.cv:
            self.cv.configure(bg=str(color) or "#000000")
            self.cv.create_rectangle(
                0, 0, self.width, self.height,
                fill=str(color) or "#000000", outline="", tags="__bg__"
            )
        return str(color)

    def rect(self, x: str, y: str, w: str, h: str,
             fill: str = "#ffffff", outline: str = "", width: str = "1") -> str:
        if not self.cv:
            return ""
        x, y, w, h = _f(x), _f(y), _f(w), _f(h)
        iid = self.cv.create_rectangle(
            x, y, x + w, y + h,
            fill=str(fill) or "#ffffff",
            outline=str(outline),
            width=_f(width, 1.0),
        )
        self._items.append(iid)
        return str(iid)

    def circle(self, cx: str, cy: str, r: str,
               fill: str = "#ffffff", outline: str = "", width: str = "1") -> str:
        if not self.cv:
            return ""
        cx, cy, r = _f(cx), _f(cy), _f(r)
        iid = self.cv.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            fill=str(fill) or "#ffffff",
            outline=str(outline),
            width=_f(width, 1.0),
        )
        self._items.append(iid)
        return str(iid)

    def ellipse(self, cx: str, cy: str, rx: str, ry: str,
                fill: str = "#ffffff", outline: str = "") -> str:
        if not self.cv:
            return ""
        cx, cy, rx, ry = _f(cx), _f(cy), _f(rx), _f(ry)
        iid = self.cv.create_oval(
            cx - rx, cy - ry, cx + rx, cy + ry,
            fill=str(fill) or "#ffffff", outline=str(outline),
        )
        self._items.append(iid)
        return str(iid)

    def line(self, x1: str, y1: str, x2: str, y2: str,
             color: str = "#ffffff", width: str = "1") -> str:
        if not self.cv:
            return ""
        iid = self.cv.create_line(
            _f(x1), _f(y1), _f(x2), _f(y2),
            fill=str(color) or "#ffffff", width=_f(width, 1.0),
        )
        self._items.append(iid)
        return str(iid)

    def polygon(self, points_csv: str,
                fill: str = "#ffffff", outline: str = "") -> str:
        if not self.cv:
            return ""
        coords = [_f(v) for v in str(points_csv).split(",") if v.strip()]
        iid = self.cv.create_polygon(
            coords, fill=str(fill) or "#ffffff", outline=str(outline),
        )
        self._items.append(iid)
        return str(iid)

    def arc(self, x: str, y: str, r: str, start: str, extent: str,
            fill: str = "", outline: str = "#ffffff", width: str = "2") -> str:
        if not self.cv:
            return ""
        x, y, r = _f(x), _f(y), _f(r)
        iid = self.cv.create_arc(
            x - r, y - r, x + r, y + r,
            start=_f(start), extent=_f(extent, 90.0),
            fill=str(fill), outline=str(outline) or "#ffffff", width=_f(width, 2.0),
        )
        self._items.append(iid)
        return str(iid)

    def draw_text(self, x: str, y: str, text: str,
                  color: str = "#ffffff", size: str = "16",
                  font: str = "Helvetica", bold: str = "false") -> str:
        if not self.cv:
            return ""
        weight = "bold" if str(bold).lower() == "true" else "normal"
        font_family = str(font) if font else "Helvetica"
        f = tkfont.Font(family=font_family, size=int(_f(size, 16.0)), weight=weight)
        iid = self.cv.create_text(
            _f(x), _f(y),
            text=str(text), fill=str(color) or "#ffffff", font=f,
        )
        self._items.append(iid)
        return str(iid)

    def image(self, x: str, y: str, path: str) -> str:
        """Draw an image file at (x, y). Supports PNG, GIF, PPM via tkinter."""
        if not self.cv:
            return ""
        try:
            img = tk.PhotoImage(file=str(path))
            if not hasattr(self, "_images"):
                self._images: list = []
            self._images.append(img)
            iid = self.cv.create_image(_f(x), _f(y), image=img, anchor="nw")
            self._items.append(iid)
            return str(iid)
        except Exception as e:
            print(f"[canvas.image] {e}")
            return ""

    # ── item manipulation ─────────────────────────────────────────────────────

    def move_item(self, item_id: str, dx: str, dy: str) -> str:
        if self.cv:
            self.cv.move(int(_f(item_id)), _f(dx), _f(dy))
        return item_id

    def delete_item(self, item_id: str) -> str:
        if self.cv:
            self.cv.delete(int(_f(item_id)))
        return item_id

    def clear(self) -> str:
        if self.cv:
            self.cv.delete("all")
            self._items.clear()
        return "cleared"

    # ── events ────────────────────────────────────────────────────────────────

    def on_click(self, callback_name: str) -> str:
        """Bind left mouse click. Verba callback receives canvas_x, canvas_y as globals."""
        if not self.cv:
            return ""
        def _handler(ev):
            try:
                env = self.interp.globals
                env.set("canvas_x", float(ev.x))
                env.set("canvas_y", float(ev.y))
                self.interp._call(str(callback_name), [], caller_env=env, line_no=0)
            except Exception as e:
                print(f"[canvas.on_click] {e}")
        self.cv.bind("<Button-1>", _handler)
        return "bound"

    def on_key(self, callback_name: str) -> str:
        """Bind key press. Verba callback receives canvas_key as global."""
        if not self.root:
            return ""
        def _handler(ev):
            try:
                env = self.interp.globals
                env.set("canvas_key", ev.keysym)
                self.interp._call(str(callback_name), [], caller_env=env, line_no=0)
            except Exception as e:
                print(f"[canvas.on_key] {e}")
        self.root.bind("<Key>", _handler)
        self.root.focus_set()
        return "bound"

    def on_motion(self, callback_name: str) -> str:
        """Bind mouse motion. Receives canvas_x, canvas_y as globals."""
        if not self.cv:
            return ""
        def _handler(ev):
            try:
                env = self.interp.globals
                env.set("canvas_x", float(ev.x))
                env.set("canvas_y", float(ev.y))
                self.interp._call(str(callback_name), [], caller_env=env, line_no=0)
            except Exception as e:
                print(f"[canvas.on_motion] {e}")
        self.cv.bind("<Motion>", _handler)
        return "bound"

    # ── animation / loop ──────────────────────────────────────────────────────

    def loop(self, callback_name: str, fps: str = "30") -> str:
        """
        Start an animation loop that calls callback_name at the given FPS.
        The loop runs until the window is closed.
        """
        if not self.root:
            return ""
        delay_ms = max(1, int(1000 / _f(fps, 30.0)))

        def _tick():
            try:
                self.interp._call(str(callback_name), [], caller_env=self.interp.globals, line_no=0)
            except Exception as e:
                print(f"[canvas.loop] {e}")
            if self.root and self.root.winfo_exists():
                self.root.after(delay_ms, _tick)

        self.root.after(delay_ms, _tick)
        self.root.mainloop()
        return "done"

    # ── output ────────────────────────────────────────────────────────────────

    def update(self) -> str:
        """Push pending draw commands to the screen without blocking."""
        if self.root:
            self.root.update()
        return "updated"

    def save(self, path: str = "canvas.ps") -> str:
        """Save canvas content as a PostScript file."""
        if self.cv:
            try:
                self.cv.postscript(file=str(path))
                return str(path)
            except Exception as e:
                print(f"[canvas.save] {e}")
        return ""

    def show(self) -> str:
        """Open the canvas window (blocking until closed)."""
        if self.root:
            self.root.mainloop()
        return "done"

    def close(self) -> str:
        if self.root:
            try:
                self.root.destroy()
            except Exception:
                pass
        return "closed"


# ── public factory ────────────────────────────────────────────────────────────

def canvas_new(title: str = "Verba Canvas",
               width: str = "800",
               height: str = "600",
               __interp__: Any = None) -> Any:
    """Create and return a new canvas window object."""
    from verba.runtime_types import NativeInstance, NativeFunction
    c = _VerbaCanvas(str(title), int(float(width)), int(float(height)), __interp__)

    methods = {
        "background": NativeFunction("background", ["color"],                         c.background),
        "rect":       NativeFunction("rect",       ["x", "y", "w", "h", "fill", "outline", "width"], c.rect),
        "circle":     NativeFunction("circle",     ["cx", "cy", "r", "fill", "outline", "width"],    c.circle),
        "ellipse":    NativeFunction("ellipse",    ["cx", "cy", "rx", "ry", "fill", "outline"],      c.ellipse),
        "line":       NativeFunction("line",       ["x1", "y1", "x2", "y2", "color", "width"],       c.line),
        "polygon":    NativeFunction("polygon",    ["points", "fill", "outline"],                     c.polygon),
        "arc":        NativeFunction("arc",        ["x", "y", "r", "start", "extent", "fill", "outline", "width"], c.arc),
        "text":       NativeFunction("text",       ["x", "y", "text", "color", "size", "font", "bold"], c.draw_text),
        "image":      NativeFunction("image",      ["x", "y", "path"],                               c.image),
        "move":       NativeFunction("move",       ["id", "dx", "dy"],                               c.move_item),
        "delete":     NativeFunction("delete",     ["id"],                                            c.delete_item),
        "clear":      NativeFunction("clear",      [],                                                c.clear),
        "on_click":   NativeFunction("on_click",   ["callback"],                                      c.on_click),
        "on_key":     NativeFunction("on_key",     ["callback"],                                      c.on_key),
        "on_motion":  NativeFunction("on_motion",  ["callback"],                                      c.on_motion),
        "loop":       NativeFunction("loop",       ["callback", "fps"],                               c.loop),
        "update":     NativeFunction("update",     [],                                                c.update),
        "save":       NativeFunction("save",       ["path"],                                          c.save),
        "show":       NativeFunction("show",       [],                                                c.show),
        "close":      NativeFunction("close",      [],                                                c.close),
    }

    ni = NativeInstance("canvas", methods)
    ni.props["width"]  = int(float(width))
    ni.props["height"] = int(float(height))
    return ni


# ── registry ──────────────────────────────────────────────────────────────────

NEEDS_INTERP = {"new"}

FUNCTIONS: dict[str, tuple] = {
    "new": (canvas_new, ["title", "width", "height"]),
}

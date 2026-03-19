import tkinter as tk
from tkinter import messagebox

def gui_alert(message, title="Verba"):
    messagebox.showinfo(title, str(message))

class _VerbaWindow:
    def __init__(self, title, interp):
        self.interp = interp
        try:
            self.root = tk.Tk()
            self.root.title(title)
            self.root.geometry("400x320")
        except Exception:
            # Headless or missing display
            self.root = None
        self.buttons = []

    def add_button(self, text, callback_name):
        if not self.root: return
        def _on_click():
            # Call back into Verba. We use globals for now.
            try:
                self.interp._call(callback_name, [], caller_env=self.interp.globals, line_no=0)
            except Exception as e:
                print(f"GUI Callback Error: {e}")
        
        btn = tk.Button(self.root, text=str(text), command=_on_click)
        btn.pack(pady=5)
        self.buttons.append(btn)

    def add_label(self, text):
        if not self.root: return
        lbl = tk.Label(self.root, text=str(text))
        lbl.pack(pady=5)

    def start(self):
        if self.root:
            self.root.mainloop()

def gui_window(title, __interp__):
    from verba.runtime_types import NativeInstance, NativeFunction
    win = _VerbaWindow(str(title), __interp__)
    
    methods = {}
    methods["button"] = NativeFunction("button", ["text", "callback"], win.add_button)
    methods["label"]  = NativeFunction("label",  ["text"],             win.add_label)
    methods["show"]   = NativeFunction("show",   [],                 win.start)
    
    return NativeInstance("gui_window", methods)

NEEDS_INTERP = {"window"}

FUNCTIONS = {
    "window": (gui_window, ["title"]),
    "alert":  (gui_alert,  ["message"]),
}

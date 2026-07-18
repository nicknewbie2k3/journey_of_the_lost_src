import json
import os
import tkinter as tk
from tkinter import messagebox

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEVEL_DIR = os.path.join(BASE_DIR, "assets", "chapter", "level")

FIELDS = [
    ("name", "Level Name"),
    ("chapter", "Chapter", 1),
    ("type", "Type", ["tutorial", "dialogue", "puzzle"]),
    ("next_scene", "Next Scene"),
]


class LevelMaker:
    def __init__(self, root):
        root.title("Hestie — Map Maker")
        root.resizable(False, False)

        frame = tk.Frame(root, padx=20, pady=20)
        frame.pack()

        tk.Label(frame, text="Level Editor", font=("", 16, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 16)
        )

        self.entries = {}

        for i, field in enumerate(FIELDS):
            key = field[0]
            label = field[1]
            default = field[2] if len(field) > 2 else ""

            tk.Label(frame, text=label + ":").grid(
                row=i + 1, column=0, sticky="e", padx=(0, 8), pady=4
            )

            if isinstance(default, list):
                var = tk.StringVar(value=default[0])
                widget = tk.OptionMenu(frame, var, *default)
                self.entries[key] = var
            elif isinstance(default, int):
                var = tk.IntVar(value=default)
                widget = tk.Spinbox(frame, from_=1, to=99, textvariable=var, width=22)
                self.entries[key] = var
            else:
                var = tk.StringVar()
                widget = tk.Entry(frame, textvariable=var, width=25)
                self.entries[key] = var

            widget.grid(row=i + 1, column=1, sticky="w", pady=4)

        tk.Button(frame, text="Create Level", command=self._export).grid(
            row=len(FIELDS) + 1, column=0, columnspan=2, pady=(16, 0)
        )

    def _export(self):
        data = {}
        for key, var in self.entries.items():
            val = var.get()
            if isinstance(val, str):
                val = val.strip()
            if isinstance(val, int) or val:
                data[key] = val

        name = data.get("name", "")
        if not name:
            messagebox.showerror("Error", "Level Name is required.")
            return

        os.makedirs(LEVEL_DIR, exist_ok=True)
        path = os.path.join(LEVEL_DIR, f"{name}.json")

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        messagebox.showinfo("Done", f"Level exported to:\n{path}")


if __name__ == "__main__":
    root = tk.Tk()
    LevelMaker(root)
    root.mainloop()

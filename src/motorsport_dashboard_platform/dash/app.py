from __future__ import annotations

import argparse
import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from .controller import DashController


class DashApplication(ttk.Frame):
    def __init__(self, master: tk.Tk, controller: DashController) -> None:
        super().__init__(master, padding=12)
        self.master = master
        self.controller = controller
        self.widget_labels: dict[str, ttk.Label] = {}
        self.alert_text: tk.Text | None = None
        self.page_label: ttk.Label | None = None
        self.pack(fill=tk.BOTH, expand=True)
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(toolbar, text="Next Page", command=self.next_page).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="Tick", command=self.refresh).pack(side=tk.LEFT, padx=4)
        self.page_label = ttk.Label(toolbar, text="")
        self.page_label.pack(side=tk.RIGHT)

        self.page_frame = ttk.Frame(self)
        self.page_frame.pack(fill=tk.BOTH, expand=True)

        alerts_frame = ttk.LabelFrame(self, text="Active Alerts")
        alerts_frame.pack(fill=tk.BOTH, expand=False, pady=(8, 0))
        self.alert_text = tk.Text(alerts_frame, height=6, wrap="word")
        self.alert_text.pack(fill=tk.BOTH, expand=True)

    def refresh(self) -> None:
        snapshot = self.controller.tick()
        for child in self.page_frame.winfo_children():
            child.destroy()
        if self.page_label is not None:
            self.page_label.configure(text=f"Page: {snapshot.page_name}")
        for index, widget in enumerate(snapshot.widgets):
            frame = ttk.LabelFrame(self.page_frame, text=widget["name"])
            frame.grid(row=index // 2, column=index % 2, sticky="nsew", padx=6, pady=6)
            ttk.Label(frame, text=widget["formatted_value"], font=("TkDefaultFont", 18, "bold")).pack(padx=16, pady=16)
            ttk.Label(frame, text=f"Signal: {widget['signal_id']} | Type: {widget['widget_type']}").pack(padx=8, pady=(0, 12))
            if widget["stale"]:
                ttk.Label(frame, text="STALE", foreground="orange").pack(pady=(0, 8))
        for column in range(2):
            self.page_frame.columnconfigure(column, weight=1)
        if self.alert_text is not None:
            self.alert_text.delete("1.0", tk.END)
            if snapshot.alerts:
                for alert in snapshot.alerts:
                    self.alert_text.insert(tk.END, f"[{alert['severity']}] {alert['message']}\n")
            else:
                self.alert_text.insert(tk.END, "No active alerts.")

    def next_page(self) -> None:
        self.controller.next_page()
        self.refresh()


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Launch the MLSW dashboard runtime.")
    parser.add_argument("--project", type=Path, help="Optional project JSON to load.")
    parser.add_argument("--headless", action="store_true", help="Run without opening the Tk UI.")
    parser.add_argument("--ticks", type=int, default=3, help="Number of headless runtime ticks.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    controller = DashController()
    if args.project:
        controller.load(args.project)
    if args.headless:
        snapshots = controller.headless_run(ticks=args.ticks)
        print(json.dumps([snapshot.__dict__ for snapshot in snapshots], indent=2))
        return 0

    root = tk.Tk()
    root.title("MLSW Dash")
    root.geometry("840x620")
    app = DashApplication(root, controller)
    root.bind("<space>", lambda *_: app.next_page())
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

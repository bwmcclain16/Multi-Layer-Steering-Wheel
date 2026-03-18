from __future__ import annotations

import argparse
import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from ..core.models import AlertDefinition, AlertSeverity, DashboardPage, DashboardProfile, SignalDefinition, SignalType, WidgetDefinition, WidgetType
from ..core.project_io import save_project
from .controller import EditorController


class EditorApplication(ttk.Frame):
    def __init__(self, master: tk.Tk, controller: EditorController) -> None:
        super().__init__(master, padding=12)
        self.master = master
        self.controller = controller
        self.pack(fill=tk.BOTH, expand=True)
        self._build_ui()
        self.refresh_all()

    def _build_ui(self) -> None:
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(toolbar, text="Load", command=self.load_project).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="Save", command=self.save_project).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="Validate", command=self.show_validation).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="Refresh JSON", command=self.refresh_json).pack(side=tk.LEFT, padx=4)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.metadata_frame = ttk.Frame(self.notebook, padding=8)
        self.signals_frame = ttk.Frame(self.notebook, padding=8)
        self.widgets_frame = ttk.Frame(self.notebook, padding=8)
        self.pages_frame = ttk.Frame(self.notebook, padding=8)
        self.alerts_frame = ttk.Frame(self.notebook, padding=8)
        self.profiles_frame = ttk.Frame(self.notebook, padding=8)
        self.json_frame = ttk.Frame(self.notebook, padding=8)
        self.validation_frame = ttk.Frame(self.notebook, padding=8)

        for name, frame in [
            ("Metadata", self.metadata_frame),
            ("Signals", self.signals_frame),
            ("Widgets", self.widgets_frame),
            ("Pages", self.pages_frame),
            ("Alerts", self.alerts_frame),
            ("Profiles", self.profiles_frame),
            ("JSON", self.json_frame),
            ("Validation", self.validation_frame),
        ]:
            self.notebook.add(frame, text=name)

        self._build_metadata_tab()
        self._build_signals_tab()
        self._build_widgets_tab()
        self._build_pages_tab()
        self._build_alerts_tab()
        self._build_profiles_tab()
        self._build_json_tab()
        self._build_validation_tab()

    def _build_metadata_tab(self) -> None:
        self.metadata_vars = {}
        for row, field_name in enumerate(["project_id", "name", "description", "version", "author"]):
            ttk.Label(self.metadata_frame, text=field_name.replace("_", " ").title()).grid(row=row, column=0, sticky=tk.W, pady=4)
            variable = tk.StringVar()
            self.metadata_vars[field_name] = variable
            ttk.Entry(self.metadata_frame, textvariable=variable, width=60).grid(row=row, column=1, sticky=tk.EW, pady=4)
        ttk.Button(self.metadata_frame, text="Apply Metadata", command=self.apply_metadata).grid(row=6, column=1, sticky=tk.E)
        self.metadata_frame.columnconfigure(1, weight=1)

    def _build_signals_tab(self) -> None:
        left = ttk.Frame(self.signals_frame)
        left.pack(side=tk.LEFT, fill=tk.Y)
        right = ttk.Frame(self.signals_frame)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12, 0))
        self.signals_list = tk.Listbox(left, height=16)
        self.signals_list.pack(fill=tk.Y)
        self.signals_list.bind("<<ListboxSelect>>", lambda *_: self.populate_signal_form())

        self.signal_vars = {name: tk.StringVar() for name in ["signal_id", "display_name", "category", "units", "format_string", "timeout_ms", "deadband", "smoothing_factor", "fallback_value"]}
        self.signal_type_var = tk.StringVar(value=SignalType.FLOAT.value)
        form_fields = ["signal_id", "display_name", "category", "units", "format_string", "timeout_ms", "deadband", "smoothing_factor", "fallback_value"]
        for row, field_name in enumerate(form_fields):
            ttk.Label(right, text=field_name.replace("_", " ").title()).grid(row=row, column=0, sticky=tk.W, pady=2)
            ttk.Entry(right, textvariable=self.signal_vars[field_name], width=40).grid(row=row, column=1, sticky=tk.EW, pady=2)
        ttk.Label(right, text="Signal Type").grid(row=len(form_fields), column=0, sticky=tk.W, pady=2)
        ttk.Combobox(right, textvariable=self.signal_type_var, values=[member.value for member in SignalType], state="readonly").grid(row=len(form_fields), column=1, sticky=tk.EW, pady=2)
        ttk.Button(right, text="Add / Update Signal", command=self.apply_signal).grid(row=len(form_fields) + 1, column=1, sticky=tk.E, pady=4)
        right.columnconfigure(1, weight=1)

    def _build_widgets_tab(self) -> None:
        self.widgets_page_var = tk.StringVar()
        controls = ttk.Frame(self.widgets_frame)
        controls.pack(fill=tk.X)
        ttk.Label(controls, text="Page").pack(side=tk.LEFT)
        self.widgets_page_combo = ttk.Combobox(controls, textvariable=self.widgets_page_var, state="readonly")
        self.widgets_page_combo.pack(side=tk.LEFT, padx=6)
        self.widgets_page_combo.bind("<<ComboboxSelected>>", lambda *_: self.refresh_widgets_list())

        body = ttk.Frame(self.widgets_frame)
        body.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        self.widgets_list = tk.Listbox(body, height=14)
        self.widgets_list.pack(side=tk.LEFT, fill=tk.Y)
        self.widgets_list.bind("<<ListboxSelect>>", lambda *_: self.populate_widget_form())

        form = ttk.Frame(body)
        form.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12, 0))
        self.widget_vars = {name: tk.StringVar() for name in ["widget_id", "name", "signal_id", "x", "y", "width", "height"]}
        self.widget_type_var = tk.StringVar(value=WidgetType.TEXT.value)
        for row, field_name in enumerate(["widget_id", "name", "signal_id", "x", "y", "width", "height"]):
            ttk.Label(form, text=field_name.replace("_", " ").title()).grid(row=row, column=0, sticky=tk.W, pady=2)
            ttk.Entry(form, textvariable=self.widget_vars[field_name], width=36).grid(row=row, column=1, sticky=tk.EW, pady=2)
        ttk.Label(form, text="Widget Type").grid(row=7, column=0, sticky=tk.W)
        ttk.Combobox(form, textvariable=self.widget_type_var, values=[member.value for member in WidgetType], state="readonly").grid(row=7, column=1, sticky=tk.EW)
        ttk.Button(form, text="Add / Update Widget", command=self.apply_widget).grid(row=8, column=1, sticky=tk.E, pady=4)
        self.canvas_preview = tk.Canvas(form, width=360, height=220, background="#08111f", highlightthickness=1, highlightbackground="#445")
        self.canvas_preview.grid(row=9, column=0, columnspan=2, sticky=tk.NSEW, pady=(10, 0))
        form.columnconfigure(1, weight=1)

    def _build_pages_tab(self) -> None:
        self.pages_list = tk.Listbox(self.pages_frame, height=10)
        self.pages_list.pack(side=tk.LEFT, fill=tk.Y)
        self.pages_list.bind("<<ListboxSelect>>", lambda *_: self.populate_page_form())
        form = ttk.Frame(self.pages_frame)
        form.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12, 0))
        self.page_vars = {name: tk.StringVar() for name in ["page_id", "name", "theme_id", "background", "grid_size"]}
        for row, field_name in enumerate(["page_id", "name", "theme_id", "background", "grid_size"]):
            ttk.Label(form, text=field_name.replace("_", " ").title()).grid(row=row, column=0, sticky=tk.W, pady=2)
            ttk.Entry(form, textvariable=self.page_vars[field_name], width=40).grid(row=row, column=1, sticky=tk.EW, pady=2)
        ttk.Button(form, text="Add / Update Page", command=self.apply_page).grid(row=6, column=1, sticky=tk.E, pady=4)
        form.columnconfigure(1, weight=1)

    def _build_alerts_tab(self) -> None:
        self.alerts_list = tk.Listbox(self.alerts_frame, height=12)
        self.alerts_list.pack(side=tk.LEFT, fill=tk.Y)
        self.alerts_list.bind("<<ListboxSelect>>", lambda *_: self.populate_alert_form())
        form = ttk.Frame(self.alerts_frame)
        form.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12, 0))
        self.alert_vars = {name: tk.StringVar() for name in ["alert_id", "name", "signal_id", "operator", "threshold", "message"]}
        self.alert_severity_var = tk.StringVar(value=AlertSeverity.WARNING.value)
        for row, field_name in enumerate(["alert_id", "name", "signal_id", "operator", "threshold", "message"]):
            ttk.Label(form, text=field_name.replace("_", " ").title()).grid(row=row, column=0, sticky=tk.W, pady=2)
            ttk.Entry(form, textvariable=self.alert_vars[field_name], width=42).grid(row=row, column=1, sticky=tk.EW, pady=2)
        ttk.Label(form, text="Severity").grid(row=6, column=0, sticky=tk.W)
        ttk.Combobox(form, textvariable=self.alert_severity_var, values=[member.value for member in AlertSeverity], state="readonly").grid(row=6, column=1, sticky=tk.EW)
        ttk.Button(form, text="Add / Update Alert", command=self.apply_alert).grid(row=7, column=1, sticky=tk.E, pady=4)
        form.columnconfigure(1, weight=1)

    def _build_profiles_tab(self) -> None:
        self.profiles_list = tk.Listbox(self.profiles_frame, height=10)
        self.profiles_list.pack(side=tk.LEFT, fill=tk.Y)
        self.profiles_list.bind("<<ListboxSelect>>", lambda *_: self.populate_profile_form())
        form = ttk.Frame(self.profiles_frame)
        form.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12, 0))
        self.profile_vars = {name: tk.StringVar() for name in ["profile_id", "name", "page_ids", "default_page_id", "enabled_backend_ids"]}
        for row, field_name in enumerate(["profile_id", "name", "page_ids", "default_page_id", "enabled_backend_ids"]):
            ttk.Label(form, text=field_name.replace("_", " ").title()).grid(row=row, column=0, sticky=tk.W, pady=2)
            ttk.Entry(form, textvariable=self.profile_vars[field_name], width=44).grid(row=row, column=1, sticky=tk.EW, pady=2)
        ttk.Button(form, text="Add / Update Profile", command=self.apply_profile).grid(row=6, column=1, sticky=tk.E, pady=4)
        form.columnconfigure(1, weight=1)

    def _build_json_tab(self) -> None:
        self.json_text = tk.Text(self.json_frame, wrap="none")
        self.json_text.pack(fill=tk.BOTH, expand=True)

    def _build_validation_tab(self) -> None:
        self.validation_text = tk.Text(self.validation_frame, wrap="word", height=12)
        self.validation_text.pack(fill=tk.BOTH, expand=True)

    def refresh_all(self) -> None:
        metadata = self.controller.project.metadata
        for field_name, variable in self.metadata_vars.items():
            variable.set(str(getattr(metadata, field_name)))
        self.signals_list.delete(0, tk.END)
        for signal in self.controller.project.signals:
            self.signals_list.insert(tk.END, signal.signal_id)
        self.pages_list.delete(0, tk.END)
        for page in self.controller.project.pages:
            self.pages_list.insert(tk.END, page.page_id)
        self.alerts_list.delete(0, tk.END)
        for alert in self.controller.project.alerts:
            self.alerts_list.insert(tk.END, alert.alert_id)
        self.profiles_list.delete(0, tk.END)
        for profile in self.controller.project.profiles:
            self.profiles_list.insert(tk.END, profile.profile_id)
        page_ids = [page.page_id for page in self.controller.project.pages]
        self.widgets_page_combo["values"] = page_ids
        if page_ids and not self.widgets_page_var.get():
            self.widgets_page_var.set(page_ids[0])
        self.refresh_widgets_list()
        self.refresh_json()
        self.show_validation()

    def refresh_widgets_list(self) -> None:
        self.widgets_list.delete(0, tk.END)
        page = next((page for page in self.controller.project.pages if page.page_id == self.widgets_page_var.get()), None)
        if not page:
            return
        for widget in page.widgets:
            self.widgets_list.insert(tk.END, widget.widget_id)
        self.draw_canvas_preview(page)

    def draw_canvas_preview(self, page: DashboardPage) -> None:
        self.canvas_preview.delete("all")
        self.canvas_preview.create_text(10, 10, text=page.name, anchor="nw", fill="#fff")
        for widget in page.widgets:
            x1, y1 = widget.x, widget.y
            x2, y2 = widget.x + widget.width, widget.y + widget.height
            self.canvas_preview.create_rectangle(x1, y1, x2, y2, outline="#ff5c39")
            self.canvas_preview.create_text(x1 + 4, y1 + 4, text=f"{widget.name}\n{widget.signal_id}", anchor="nw", fill="#f2f7ff")

    def refresh_json(self) -> None:
        self.json_text.delete("1.0", tk.END)
        self.json_text.insert(tk.END, self.controller.export_json())

    def show_validation(self) -> None:
        issues = self.controller.validate()
        self.validation_text.delete("1.0", tk.END)
        if not issues:
            self.validation_text.insert(tk.END, "No validation issues detected.")
            return
        for issue in issues:
            self.validation_text.insert(tk.END, f"[{issue.level}] {issue.path}: {issue.message}\n")

    def apply_metadata(self) -> None:
        self.controller.update_metadata(**{name: var.get() for name, var in self.metadata_vars.items()})
        self.refresh_all()

    def apply_signal(self) -> None:
        signal = SignalDefinition(
            signal_id=self.signal_vars["signal_id"].get(),
            display_name=self.signal_vars["display_name"].get(),
            category=self.signal_vars["category"].get(),
            signal_type=SignalType(self.signal_type_var.get()),
            units=self.signal_vars["units"].get(),
            format_string=self.signal_vars["format_string"].get() or "{value}",
            timeout_ms=int(self.signal_vars["timeout_ms"].get() or 1000),
            deadband=float(self.signal_vars["deadband"].get() or 0.0),
            smoothing_factor=float(self.signal_vars["smoothing_factor"].get() or 0.0),
            fallback_value=self.signal_vars["fallback_value"].get() or None,
        )
        self.controller.upsert_signal(signal)
        self.refresh_all()

    def apply_widget(self) -> None:
        if not self.widgets_page_var.get():
            return
        widget = WidgetDefinition(
            widget_id=self.widget_vars["widget_id"].get(),
            name=self.widget_vars["name"].get(),
            widget_type=WidgetType(self.widget_type_var.get()),
            signal_id=self.widget_vars["signal_id"].get(),
            x=int(self.widget_vars["x"].get() or 0),
            y=int(self.widget_vars["y"].get() or 0),
            width=int(self.widget_vars["width"].get() or 100),
            height=int(self.widget_vars["height"].get() or 60),
        )
        self.controller.upsert_widget(self.widgets_page_var.get(), widget)
        self.refresh_all()

    def apply_page(self) -> None:
        page = DashboardPage(
            page_id=self.page_vars["page_id"].get(),
            name=self.page_vars["name"].get(),
            theme_id=self.page_vars["theme_id"].get(),
            background=self.page_vars["background"].get() or "#08111f",
            grid_size=int(self.page_vars["grid_size"].get() or 20),
        )
        existing = next((item for item in self.controller.project.pages if item.page_id == page.page_id), None)
        if existing:
            page.widgets = existing.widgets
        self.controller.upsert_page(page)
        self.refresh_all()

    def apply_alert(self) -> None:
        raw_threshold = self.alert_vars["threshold"].get()
        try:
            threshold = float(raw_threshold)
        except ValueError:
            threshold = raw_threshold
        alert = AlertDefinition(
            alert_id=self.alert_vars["alert_id"].get(),
            name=self.alert_vars["name"].get(),
            signal_id=self.alert_vars["signal_id"].get(),
            operator=self.alert_vars["operator"].get() or ">=",
            threshold=threshold,
            severity=AlertSeverity(self.alert_severity_var.get()),
            message=self.alert_vars["message"].get() or "Alert triggered",
        )
        self.controller.upsert_alert(alert)
        self.refresh_all()

    def apply_profile(self) -> None:
        page_ids = [item.strip() for item in self.profile_vars["page_ids"].get().split(",") if item.strip()]
        backend_ids = [item.strip() for item in self.profile_vars["enabled_backend_ids"].get().split(",") if item.strip()]
        profile = DashboardProfile(
            profile_id=self.profile_vars["profile_id"].get(),
            name=self.profile_vars["name"].get(),
            page_ids=page_ids,
            default_page_id=self.profile_vars["default_page_id"].get(),
            enabled_backend_ids=backend_ids,
        )
        self.controller.upsert_profile(profile)
        self.refresh_all()

    def populate_signal_form(self) -> None:
        selection = self.signals_list.curselection()
        if not selection:
            return
        signal = self.controller.project.signals[selection[0]]
        for field_name, variable in self.signal_vars.items():
            variable.set(str(getattr(signal, field_name)))
        self.signal_type_var.set(signal.signal_type.value)

    def populate_widget_form(self) -> None:
        selection = self.widgets_list.curselection()
        page = next((page for page in self.controller.project.pages if page.page_id == self.widgets_page_var.get()), None)
        if not selection or not page:
            return
        widget = page.widgets[selection[0]]
        for field_name, variable in self.widget_vars.items():
            variable.set(str(getattr(widget, field_name)))
        self.widget_type_var.set(widget.widget_type.value)

    def populate_page_form(self) -> None:
        selection = self.pages_list.curselection()
        if not selection:
            return
        page = self.controller.project.pages[selection[0]]
        for field_name, variable in self.page_vars.items():
            variable.set(str(getattr(page, field_name)))

    def populate_alert_form(self) -> None:
        selection = self.alerts_list.curselection()
        if not selection:
            return
        alert = self.controller.project.alerts[selection[0]]
        for field_name, variable in self.alert_vars.items():
            variable.set(str(getattr(alert, field_name)))
        self.alert_severity_var.set(alert.severity.value)

    def populate_profile_form(self) -> None:
        selection = self.profiles_list.curselection()
        if not selection:
            return
        profile = self.controller.project.profiles[selection[0]]
        self.profile_vars["profile_id"].set(profile.profile_id)
        self.profile_vars["name"].set(profile.name)
        self.profile_vars["page_ids"].set(", ".join(profile.page_ids))
        self.profile_vars["default_page_id"].set(profile.default_page_id)
        self.profile_vars["enabled_backend_ids"].set(", ".join(profile.enabled_backend_ids))

    def load_project(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not path:
            return
        self.controller.load(path)
        self.refresh_all()

    def save_project(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not path:
            return
        self.controller.save(path)
        messagebox.showinfo("Saved", f"Project saved to {path}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Launch the MLSW editor application.")
    parser.add_argument("--project", type=Path, help="Optional project JSON to load.")
    parser.add_argument("--headless", action="store_true", help="Run without opening the Tk UI.")
    parser.add_argument("--validate", action="store_true", help="Print validation output in headless mode.")
    parser.add_argument("--export-json", action="store_true", help="Print project JSON in headless mode.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    controller = EditorController()
    if args.project:
        controller.load(args.project)
    if args.headless:
        if args.validate:
            issues = controller.validate()
            if issues:
                for issue in issues:
                    print(f"[{issue.level}] {issue.path}: {issue.message}")
            else:
                print("No validation issues detected.")
        if args.export_json:
            print(controller.export_json())
        return 0

    root = tk.Tk()
    root.title("MLSW Editor")
    root.geometry("1000x760")
    EditorApplication(root, controller)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

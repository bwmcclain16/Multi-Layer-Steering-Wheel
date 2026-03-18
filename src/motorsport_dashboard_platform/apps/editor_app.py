from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path

from ..example_project import EXAMPLE_PROJECT, create_example_project
from ..models import (
    AlertDefinition,
    AlertScope,
    AlertSeverity,
    DashboardProject,
    FallbackMode,
    LatchBehavior,
    LayoutAnchor,
    PageDefinition,
    PageType,
    ProfileDefinition,
    Resolution,
    SignalDataType,
    SignalDefinition,
    SignalFallbackPolicy,
    SignalFreshnessPolicy,
    WidgetBinding,
    WidgetDataBehavior,
    WidgetDataStateBehavior,
    WidgetDefinition,
    WidgetLayout,
)
from ..project_io import load_project, save_project
from ..validation import ProjectValidator


class EditorController:
    def __init__(self, project: DashboardProject | None = None):
        self.project = project or create_example_project()
        self.validator = ProjectValidator()

    def load(self, path: str | Path) -> DashboardProject:
        self.project = load_project(path)
        return self.project

    def reset_example(self) -> DashboardProject:
        self.project = create_example_project()
        return self.project

    def save(self, path: str | Path) -> None:
        save_project(self.project, path, pretty=True)

    def validate(self) -> list[str]:
        report = self.validator.validate(self.project)
        if report.is_valid:
            return ["Project is valid."]
        return [f"[{issue.level}] {issue.path}: {issue.message}" for issue in report.issues]

    def to_pretty_json(self) -> str:
        return json.dumps(self.project.to_dict(), indent=2)

    def update_metadata(self, *, name: str | None = None, description: str | None = None, version: str | None = None) -> DashboardProject:
        metadata = self.project.metadata
        self.project.metadata = replace(
            metadata,
            name=name if name is not None else metadata.name,
            description=description if description is not None else metadata.description,
            version=version if version is not None else metadata.version,
        )
        return self.project

    def _upsert(self, collection: list, item, item_id: str) -> None:
        for index, existing in enumerate(collection):
            if existing.id == item_id:
                collection[index] = item
                return
        collection.append(item)

    def upsert_signal(
        self,
        *,
        signal_id: str,
        display_name: str,
        category: str,
        data_type: str,
        units: str = "",
        stale_after_ms: int | None = None,
        missing_after_ms: int | None = None,
        fallback_mode: str = "freeze-last",
        fallback_value: str = "",
    ) -> SignalDefinition:
        signal = SignalDefinition(
            id=signal_id,
            display_name=display_name,
            category=category,
            data_type=SignalDataType(data_type),
            units=units or None,
            freshness=SignalFreshnessPolicy(stale_after_ms=stale_after_ms, missing_after_ms=missing_after_ms),
            fallback=SignalFallbackPolicy(mode=FallbackMode(fallback_mode), default_value=fallback_value or None),
        )
        self._upsert(self.project.signals, signal, signal_id)
        return signal

    def create_signal(self) -> SignalDefinition:
        base_id = f"custom.signal.{len(self.project.signals) + 1}"
        signal = SignalDefinition(
            id=base_id,
            display_name=f"Custom Signal {len(self.project.signals) + 1}",
            category="custom",
            data_type=SignalDataType.NUMBER,
            freshness=SignalFreshnessPolicy(stale_after_ms=500, missing_after_ms=1500),
            fallback=SignalFallbackPolicy(mode=FallbackMode.FREEZE_LAST),
        )
        self.project.signals.append(signal)
        return signal

    def upsert_widget(
        self,
        *,
        widget_id: str,
        name: str,
        widget_type: str,
        x: int,
        y: int,
        width: int,
        height: int,
        anchor: str,
        binding_signal_id: str,
        page_id: str | None,
    ) -> WidgetDefinition:
        widget = WidgetDefinition(
            id=widget_id,
            type=widget_type,
            name=name,
            layout=WidgetLayout(x=x, y=y, width=width, height=height, anchor=LayoutAnchor(anchor)),
            bindings=[WidgetBinding(key="value", signal_id=binding_signal_id)] if binding_signal_id else [],
            data_behavior=WidgetDataBehavior(
                on_stale=WidgetDataStateBehavior.GRAY_OUT,
                on_missing=WidgetDataStateBehavior.PLACEHOLDER,
                placeholder_text="---",
            ),
        )
        self._upsert(self.project.widgets, widget, widget_id)
        if page_id:
            self.assign_widget_to_page(page_id=page_id, widget_id=widget_id)
        return widget

    def create_widget(self, *, page_id: str | None = None) -> WidgetDefinition:
        widget_id = f"widget-custom-{len(self.project.widgets) + 1}"
        signal_id = self.project.signals[0].id if self.project.signals else ""
        widget = self.upsert_widget(
            widget_id=widget_id,
            name=f"Widget {len(self.project.widgets) + 1}",
            widget_type="numeric-readout",
            x=40,
            y=40,
            width=160,
            height=60,
            anchor="top-left",
            binding_signal_id=signal_id,
            page_id=page_id,
        )
        return widget

    def assign_widget_to_page(self, *, page_id: str, widget_id: str) -> None:
        for index, page in enumerate(self.project.pages):
            if page.id == page_id:
                widget_ids = list(page.widget_ids)
                if widget_id not in widget_ids:
                    widget_ids.append(widget_id)
                self.project.pages[index] = replace(page, widget_ids=widget_ids)
                return

    def upsert_page(self, *, page_id: str, name: str, width: int, height: int, background_color: str, widget_ids_csv: str) -> PageDefinition:
        widget_ids = [item.strip() for item in widget_ids_csv.split(",") if item.strip()]
        page = PageDefinition(
            id=page_id,
            name=name,
            reference_resolution=Resolution(width=width, height=height),
            type=PageType.DASHBOARD,
            background=None,
            widget_ids=widget_ids,
        )
        if background_color:
            from ..models import BackgroundDefinition

            page = replace(page, background=BackgroundDefinition(color=background_color))
        self._upsert(self.project.pages, page, page_id)
        return page

    def create_page(self) -> PageDefinition:
        page_id = f"page-custom-{len(self.project.pages) + 1}"
        page = PageDefinition(
            id=page_id,
            name=f"Custom Page {len(self.project.pages) + 1}",
            reference_resolution=Resolution(width=800, height=480),
            widget_ids=[],
        )
        self.project.pages.append(page)
        return page

    def upsert_alert(self, *, alert_id: str, name: str, severity: str, priority: int, condition: str) -> AlertDefinition:
        alert = AlertDefinition(
            id=alert_id,
            name=name,
            severity=AlertSeverity(severity),
            priority=priority,
            scope=AlertScope.PROFILE,
            condition=condition,
            latch_behavior=LatchBehavior.NONE,
        )
        self._upsert(self.project.alerts, alert, alert_id)
        return alert

    def create_alert(self) -> AlertDefinition:
        alert_id = f"alert-custom-{len(self.project.alerts) + 1}"
        alert = AlertDefinition(
            id=alert_id,
            name=f"Custom Alert {len(self.project.alerts) + 1}",
            severity=AlertSeverity.WARNING,
            priority=50,
            scope=AlertScope.PROFILE,
            condition="signal('vehicle.engine.rpm') > 9000",
        )
        self.project.alerts.append(alert)
        return alert

    def upsert_profile(
        self,
        *,
        profile_id: str,
        name: str,
        default_page_id: str,
        theme_id: str,
        page_ids_csv: str,
        alert_ids_csv: str,
        backend_ids_csv: str,
        tags_csv: str,
    ) -> ProfileDefinition:
        page_ids = [item.strip() for item in page_ids_csv.split(",") if item.strip()]
        alert_ids = [item.strip() for item in alert_ids_csv.split(",") if item.strip()]
        backend_ids = [item.strip() for item in backend_ids_csv.split(",") if item.strip()]
        tags = [item.strip() for item in tags_csv.split(",") if item.strip()]
        mapping_ids = [mapping.id for mapping in self.project.mappings]
        profile = ProfileDefinition(
            id=profile_id,
            name=name,
            backend_ids=backend_ids,
            mapping_ids=mapping_ids,
            page_ids=page_ids or ([default_page_id] if default_page_id else []),
            default_page_id=default_page_id,
            theme_id=theme_id,
            alert_ids=alert_ids,
            tags=tags,
        )
        self._upsert(self.project.profiles, profile, profile_id)
        return profile

    def create_profile(self) -> ProfileDefinition:
        page_id = self.project.pages[0].id if self.project.pages else ""
        theme_id = self.project.themes[0].id if self.project.themes else ""
        backend_ids = [backend.id for backend in self.project.backends[:1]]
        profile = ProfileDefinition(
            id=f"profile-custom-{len(self.project.profiles) + 1}",
            name=f"Custom Profile {len(self.project.profiles) + 1}",
            backend_ids=backend_ids,
            mapping_ids=[mapping.id for mapping in self.project.mappings],
            page_ids=[page_id] if page_id else [],
            default_page_id=page_id,
            theme_id=theme_id,
            tags=["custom"],
        )
        self.project.profiles.append(profile)
        return profile


class EditorApplication:
    def __init__(self, controller: EditorController | None = None):
        self.controller = controller or EditorController()

    def run(self, *, source: str | None = None) -> None:
        if source:
            self.controller.load(source)
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk

        root = tk.Tk()
        root.title("MLSW Visual Editor")
        root.geometry("1400x900")

        toolbar = ttk.Frame(root, padding=10)
        toolbar.pack(fill="x")
        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        metadata_name = tk.StringVar(value=self.controller.project.metadata.name)
        metadata_version = tk.StringVar(value=self.controller.project.metadata.version)
        metadata_description = tk.StringVar(value=self.controller.project.metadata.description or "")

        signal_vars = {key: tk.StringVar() for key in ["id", "display_name", "category", "data_type", "units", "stale_after_ms", "missing_after_ms", "fallback_mode", "fallback_value"]}
        widget_vars = {key: tk.StringVar() for key in ["id", "name", "type", "x", "y", "width", "height", "anchor", "binding_signal_id", "page_id"]}
        page_vars = {key: tk.StringVar() for key in ["id", "name", "width", "height", "background_color", "widget_ids"]}
        alert_vars = {key: tk.StringVar() for key in ["id", "name", "severity", "priority", "condition"]}
        profile_vars = {key: tk.StringVar() for key in ["id", "name", "default_page_id", "theme_id", "page_ids", "alert_ids", "backend_ids", "tags"]}

        overview_frame = ttk.Frame(notebook, padding=12)
        signals_frame = ttk.Frame(notebook, padding=12)
        widgets_frame = ttk.Frame(notebook, padding=12)
        pages_frame = ttk.Frame(notebook, padding=12)
        alerts_frame = ttk.Frame(notebook, padding=12)
        profiles_frame = ttk.Frame(notebook, padding=12)
        json_frame = ttk.Frame(notebook, padding=12)

        notebook.add(overview_frame, text="Overview")
        notebook.add(signals_frame, text="Signals")
        notebook.add(widgets_frame, text="Widgets")
        notebook.add(pages_frame, text="Pages")
        notebook.add(alerts_frame, text="Alerts")
        notebook.add(profiles_frame, text="Profiles")
        notebook.add(json_frame, text="JSON")

        validation_text = tk.Text(overview_frame, width=80, height=12)
        json_text = tk.Text(json_frame, wrap="none")
        json_text.pack(fill="both", expand=True)

        signal_list = tk.Listbox(signals_frame, exportselection=False)
        widget_list = tk.Listbox(widgets_frame, exportselection=False)
        page_list = tk.Listbox(pages_frame, exportselection=False)
        alert_list = tk.Listbox(alerts_frame, exportselection=False)
        profile_list = tk.Listbox(profiles_frame, exportselection=False)
        canvas = tk.Canvas(widgets_frame, width=800, height=480, background="#05070A")

        def refresh_json() -> None:
            json_text.delete("1.0", tk.END)
            json_text.insert(tk.END, self.controller.to_pretty_json())

        def refresh_validation() -> None:
            validation_text.delete("1.0", tk.END)
            validation_text.insert(tk.END, "\n".join(self.controller.validate()))

        def refresh_overview() -> None:
            self.controller.update_metadata(
                name=metadata_name.get(),
                version=metadata_version.get(),
                description=metadata_description.get(),
            )
            refresh_validation()
            refresh_json()

        def fill_listbox(listbox: tk.Listbox, items: list[str]) -> None:
            listbox.delete(0, tk.END)
            for item in items:
                listbox.insert(tk.END, item)

        def refresh_signals() -> None:
            fill_listbox(signal_list, [f"{signal.id} — {signal.display_name}" for signal in self.controller.project.signals])
            refresh_json()
            refresh_validation()

        def load_selected_signal(*_args) -> None:
            if not signal_list.curselection():
                return
            signal = self.controller.project.signals[signal_list.curselection()[0]]
            signal_vars["id"].set(signal.id)
            signal_vars["display_name"].set(signal.display_name)
            signal_vars["category"].set(signal.category)
            signal_vars["data_type"].set(str(signal.data_type))
            signal_vars["units"].set(signal.units or "")
            signal_vars["stale_after_ms"].set(str(signal.freshness.stale_after_ms if signal.freshness and signal.freshness.stale_after_ms is not None else ""))
            signal_vars["missing_after_ms"].set(str(signal.freshness.missing_after_ms if signal.freshness and signal.freshness.missing_after_ms is not None else ""))
            signal_vars["fallback_mode"].set(str(signal.fallback.mode if signal.fallback else "freeze-last"))
            signal_vars["fallback_value"].set("" if not signal.fallback or signal.fallback.default_value is None else str(signal.fallback.default_value))

        def save_signal() -> None:
            self.controller.upsert_signal(
                signal_id=signal_vars["id"].get(),
                display_name=signal_vars["display_name"].get(),
                category=signal_vars["category"].get(),
                data_type=signal_vars["data_type"].get() or "number",
                units=signal_vars["units"].get(),
                stale_after_ms=_int_or_none(signal_vars["stale_after_ms"].get()),
                missing_after_ms=_int_or_none(signal_vars["missing_after_ms"].get()),
                fallback_mode=signal_vars["fallback_mode"].get() or "freeze-last",
                fallback_value=signal_vars["fallback_value"].get(),
            )
            refresh_signals()
            refresh_widgets()

        def refresh_widgets() -> None:
            fill_listbox(widget_list, [f"{widget.id} — {widget.name}" for widget in self.controller.project.widgets])
            refresh_canvas()
            refresh_json()
            refresh_validation()

        def refresh_canvas() -> None:
            canvas.delete("all")
            page_id = widget_vars["page_id"].get() or (self.controller.project.pages[0].id if self.controller.project.pages else "")
            page = next((page for page in self.controller.project.pages if page.id == page_id), None)
            if page and page.background and page.background.color:
                canvas.configure(background=page.background.color)
            else:
                canvas.configure(background="#05070A")
            for widget in self.controller.project.widgets:
                if page and widget.id not in page.widget_ids:
                    continue
                x1 = widget.layout.x
                y1 = widget.layout.y
                x2 = x1 + widget.layout.width
                y2 = y1 + widget.layout.height
                canvas.create_rectangle(x1, y1, x2, y2, outline="#00D1FF", width=2)
                canvas.create_text(x1 + 8, y1 + 8, anchor="nw", text=widget.name, fill="white")

        def load_selected_widget(*_args) -> None:
            if not widget_list.curselection():
                return
            widget = self.controller.project.widgets[widget_list.curselection()[0]]
            widget_vars["id"].set(widget.id)
            widget_vars["name"].set(widget.name)
            widget_vars["type"].set(widget.type)
            widget_vars["x"].set(str(widget.layout.x))
            widget_vars["y"].set(str(widget.layout.y))
            widget_vars["width"].set(str(widget.layout.width))
            widget_vars["height"].set(str(widget.layout.height))
            widget_vars["anchor"].set(str(widget.layout.anchor))
            widget_vars["binding_signal_id"].set(widget.bindings[0].signal_id if widget.bindings else "")
            widget_vars["page_id"].set(_find_page_id_for_widget(widget.id, self.controller.project.pages))
            refresh_canvas()

        def save_widget() -> None:
            self.controller.upsert_widget(
                widget_id=widget_vars["id"].get(),
                name=widget_vars["name"].get(),
                widget_type=widget_vars["type"].get() or "numeric-readout",
                x=_int_or_default(widget_vars["x"].get(), 0),
                y=_int_or_default(widget_vars["y"].get(), 0),
                width=_int_or_default(widget_vars["width"].get(), 120),
                height=_int_or_default(widget_vars["height"].get(), 60),
                anchor=widget_vars["anchor"].get() or "top-left",
                binding_signal_id=widget_vars["binding_signal_id"].get(),
                page_id=widget_vars["page_id"].get() or None,
            )
            refresh_widgets()
            refresh_pages()

        def refresh_pages() -> None:
            fill_listbox(page_list, [f"{page.id} — {page.name}" for page in self.controller.project.pages])
            refresh_canvas()
            refresh_json()
            refresh_validation()

        def load_selected_page(*_args) -> None:
            if not page_list.curselection():
                return
            page = self.controller.project.pages[page_list.curselection()[0]]
            page_vars["id"].set(page.id)
            page_vars["name"].set(page.name)
            page_vars["width"].set(str(page.reference_resolution.width))
            page_vars["height"].set(str(page.reference_resolution.height))
            page_vars["background_color"].set(page.background.color if page.background and page.background.color else "")
            page_vars["widget_ids"].set(", ".join(page.widget_ids))
            widget_vars["page_id"].set(page.id)
            refresh_canvas()

        def save_page() -> None:
            self.controller.upsert_page(
                page_id=page_vars["id"].get(),
                name=page_vars["name"].get(),
                width=_int_or_default(page_vars["width"].get(), 800),
                height=_int_or_default(page_vars["height"].get(), 480),
                background_color=page_vars["background_color"].get(),
                widget_ids_csv=page_vars["widget_ids"].get(),
            )
            refresh_pages()
            refresh_widgets()

        def refresh_alerts() -> None:
            fill_listbox(alert_list, [f"{alert.id} — {alert.name}" for alert in self.controller.project.alerts])
            refresh_json()
            refresh_validation()

        def load_selected_alert(*_args) -> None:
            if not alert_list.curselection():
                return
            alert = self.controller.project.alerts[alert_list.curselection()[0]]
            alert_vars["id"].set(alert.id)
            alert_vars["name"].set(alert.name)
            alert_vars["severity"].set(str(alert.severity))
            alert_vars["priority"].set(str(alert.priority))
            alert_vars["condition"].set(alert.condition)

        def save_alert() -> None:
            self.controller.upsert_alert(
                alert_id=alert_vars["id"].get(),
                name=alert_vars["name"].get(),
                severity=alert_vars["severity"].get() or "warning",
                priority=_int_or_default(alert_vars["priority"].get(), 50),
                condition=alert_vars["condition"].get(),
            )
            refresh_alerts()
            refresh_profiles()

        def refresh_profiles() -> None:
            fill_listbox(profile_list, [f"{profile.id} — {profile.name}" for profile in self.controller.project.profiles])
            refresh_json()
            refresh_validation()

        def load_selected_profile(*_args) -> None:
            if not profile_list.curselection():
                return
            profile = self.controller.project.profiles[profile_list.curselection()[0]]
            profile_vars["id"].set(profile.id)
            profile_vars["name"].set(profile.name)
            profile_vars["default_page_id"].set(profile.default_page_id)
            profile_vars["theme_id"].set(profile.theme_id)
            profile_vars["page_ids"].set(", ".join(profile.page_ids))
            profile_vars["alert_ids"].set(", ".join(profile.alert_ids))
            profile_vars["backend_ids"].set(", ".join(profile.backend_ids))
            profile_vars["tags"].set(", ".join(profile.tags))

        def save_profile() -> None:
            self.controller.upsert_profile(
                profile_id=profile_vars["id"].get(),
                name=profile_vars["name"].get(),
                default_page_id=profile_vars["default_page_id"].get(),
                theme_id=profile_vars["theme_id"].get() or (self.controller.project.themes[0].id if self.controller.project.themes else ""),
                page_ids_csv=profile_vars["page_ids"].get(),
                alert_ids_csv=profile_vars["alert_ids"].get(),
                backend_ids_csv=profile_vars["backend_ids"].get(),
                tags_csv=profile_vars["tags"].get(),
            )
            refresh_profiles()

        def load_project_from_disk() -> None:
            file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*")])
            if not file_path:
                return
            self.controller.load(file_path)
            metadata_name.set(self.controller.project.metadata.name)
            metadata_version.set(self.controller.project.metadata.version)
            metadata_description.set(self.controller.project.metadata.description or "")
            refresh_all()

        def save_project_to_disk() -> None:
            refresh_overview()
            file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
            if not file_path:
                return
            self.controller.save(file_path)
            messagebox.showinfo("Saved", f"Project saved to {file_path}")

        def reset_example() -> None:
            self.controller.reset_example()
            metadata_name.set(self.controller.project.metadata.name)
            metadata_version.set(self.controller.project.metadata.version)
            metadata_description.set(self.controller.project.metadata.description or "")
            refresh_all()

        def refresh_all() -> None:
            refresh_overview()
            refresh_signals()
            refresh_widgets()
            refresh_pages()
            refresh_alerts()
            refresh_profiles()

        ttk.Button(toolbar, text="Load JSON", command=load_project_from_disk).pack(side="left")
        ttk.Button(toolbar, text="Save JSON", command=save_project_to_disk).pack(side="left", padx=6)
        ttk.Button(toolbar, text="Reset Example", command=reset_example).pack(side="left", padx=6)
        ttk.Button(toolbar, text="Refresh All", command=refresh_all).pack(side="left", padx=6)

        _build_overview_tab(overview_frame, metadata_name, metadata_version, metadata_description, validation_text, refresh_overview)
        _build_entity_editor_tab(signals_frame, signal_list, signal_vars, load_selected_signal, save_signal, lambda: [self.controller.create_signal(), refresh_signals()])
        _build_widget_tab(widgets_frame, widget_list, widget_vars, canvas, load_selected_widget, save_widget, lambda: [self.controller.create_widget(page_id=widget_vars["page_id"].get() or (self.controller.project.pages[0].id if self.controller.project.pages else None)), refresh_widgets()])
        _build_entity_editor_tab(pages_frame, page_list, page_vars, load_selected_page, save_page, lambda: [self.controller.create_page(), refresh_pages()])
        _build_entity_editor_tab(alerts_frame, alert_list, alert_vars, load_selected_alert, save_alert, lambda: [self.controller.create_alert(), refresh_alerts()])
        _build_entity_editor_tab(profiles_frame, profile_list, profile_vars, load_selected_profile, save_profile, lambda: [self.controller.create_profile(), refresh_profiles()])

        signal_list.bind("<<ListboxSelect>>", load_selected_signal)
        widget_list.bind("<<ListboxSelect>>", load_selected_widget)
        page_list.bind("<<ListboxSelect>>", load_selected_page)
        alert_list.bind("<<ListboxSelect>>", load_selected_alert)
        profile_list.bind("<<ListboxSelect>>", load_selected_profile)

        refresh_all()
        root.mainloop()


def _build_overview_tab(frame, metadata_name, metadata_version, metadata_description, validation_text, refresh_callback) -> None:
    from tkinter import ttk

    form = ttk.Frame(frame)
    form.pack(fill="x")
    ttk.Label(form, text="Project Name").grid(row=0, column=0, sticky="w")
    ttk.Entry(form, textvariable=metadata_name, width=40).grid(row=0, column=1, sticky="ew", padx=6)
    ttk.Label(form, text="Version").grid(row=0, column=2, sticky="w")
    ttk.Entry(form, textvariable=metadata_version, width=16).grid(row=0, column=3, sticky="w", padx=6)
    ttk.Label(form, text="Description").grid(row=1, column=0, sticky="w")
    ttk.Entry(form, textvariable=metadata_description, width=90).grid(row=1, column=1, columnspan=3, sticky="ew", padx=6)
    ttk.Button(form, text="Apply Metadata", command=refresh_callback).grid(row=0, column=4, rowspan=2, padx=8)
    form.columnconfigure(1, weight=1)

    ttk.Label(frame, text="Validation Output", font=("Arial", 12, "bold")).pack(anchor="w", pady=(12, 4))
    validation_text.pack(fill="both", expand=True)


def _build_entity_editor_tab(frame, listbox, vars_map, select_callback, save_callback, add_callback) -> None:
    from tkinter import ttk

    left = ttk.Frame(frame)
    left.pack(side="left", fill="y")
    right = ttk.Frame(frame)
    right.pack(side="left", fill="both", expand=True, padx=(12, 0))

    listbox.pack(in_=left, fill="y", expand=True)
    ttk.Button(left, text="New", command=add_callback).pack(fill="x", pady=4)
    ttk.Button(left, text="Save", command=save_callback).pack(fill="x")

    row = 0
    for key, variable in vars_map.items():
        ttk.Label(right, text=key.replace("_", " ").title()).grid(row=row, column=0, sticky="w", pady=4)
        ttk.Entry(right, textvariable=variable, width=60).grid(row=row, column=1, sticky="ew", padx=6)
        row += 1
    ttk.Button(right, text="Apply Changes", command=save_callback).grid(row=row, column=0, columnspan=2, sticky="w", pady=8)
    right.columnconfigure(1, weight=1)


def _build_widget_tab(frame, listbox, vars_map, canvas, select_callback, save_callback, add_callback) -> None:
    from tkinter import ttk

    top = ttk.Frame(frame)
    top.pack(fill="both", expand=True)
    left = ttk.Frame(top)
    left.pack(side="left", fill="y")
    middle = ttk.Frame(top)
    middle.pack(side="left", fill="both", expand=True, padx=(12, 12))
    right = ttk.Frame(top)
    right.pack(side="left", fill="both", expand=True)

    listbox.pack(in_=left, fill="y", expand=True)
    ttk.Button(left, text="New", command=add_callback).pack(fill="x", pady=4)
    ttk.Button(left, text="Save", command=save_callback).pack(fill="x")

    row = 0
    for key, variable in vars_map.items():
        ttk.Label(middle, text=key.replace("_", " ").title()).grid(row=row, column=0, sticky="w", pady=4)
        ttk.Entry(middle, textvariable=variable, width=40).grid(row=row, column=1, sticky="ew", padx=6)
        row += 1
    ttk.Button(middle, text="Apply Changes", command=save_callback).grid(row=row, column=0, columnspan=2, sticky="w", pady=8)
    middle.columnconfigure(1, weight=1)

    ttk.Label(right, text="Page Canvas Preview", font=("Arial", 12, "bold")).pack(anchor="w")
    canvas.pack(fill="both", expand=True)


def _int_or_none(value: str) -> int | None:
    return int(value) if value.strip() else None


def _int_or_default(value: str, default: int) -> int:
    return int(value) if value.strip() else default


def _find_page_id_for_widget(widget_id: str, pages: list[PageDefinition]) -> str:
    for page in pages:
        if widget_id in page.widget_ids:
            return page.id
    return ""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mlsw-editor", description="Run the MLSW editor application")
    parser.add_argument("--project", help="Optional project JSON to load")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode and print a summary")
    parser.add_argument("--validate", action="store_true", help="Validate the loaded project and print results")
    parser.add_argument("--dump-json", action="store_true", help="Print the loaded project JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    controller = EditorController(EXAMPLE_PROJECT)
    if args.project:
        controller.load(args.project)

    if args.headless or args.validate or args.dump_json:
        if args.validate:
            for line in controller.validate():
                print(line)
        else:
            project = controller.project
            print(f"Project: {project.metadata.name}")
            print(f"Profiles: {len(project.profiles)}")
            print(f"Pages: {len(project.pages)}")
            print(f"Signals: {len(project.signals)}")
        if args.dump_json:
            print(controller.to_pretty_json())
        return 0

    EditorApplication(controller).run(source=args.project)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from ..core.example_project import build_example_project
from ..core.models import AlertDefinition, DashboardPage, DashboardProfile, DashboardProject, SignalDefinition, WidgetDefinition
from ..core.project_io import load_project, save_project
from ..core.validation import ValidationIssue, validate_project


class EditorController:
    def __init__(self, project: DashboardProject | None = None) -> None:
        self.project = project or build_example_project()

    def load(self, path: str | Path) -> DashboardProject:
        self.project = load_project(path)
        return self.project

    def save(self, path: str | Path) -> None:
        save_project(self.project, path)

    def export_json(self) -> str:
        return json.dumps(self.project.to_dict(), indent=2, sort_keys=True)

    def validate(self) -> List[ValidationIssue]:
        return validate_project(self.project)

    def update_metadata(self, **values: str) -> None:
        for key, value in values.items():
            if hasattr(self.project.metadata, key):
                setattr(self.project.metadata, key, value)

    def upsert_signal(self, signal: SignalDefinition) -> None:
        self._upsert_by_attr(self.project.signals, signal, "signal_id")

    def upsert_page(self, page: DashboardPage) -> None:
        self._upsert_by_attr(self.project.pages, page, "page_id")

    def upsert_alert(self, alert: AlertDefinition) -> None:
        self._upsert_by_attr(self.project.alerts, alert, "alert_id")

    def upsert_profile(self, profile: DashboardProfile) -> None:
        self._upsert_by_attr(self.project.profiles, profile, "profile_id")

    def upsert_widget(self, page_id: str, widget: WidgetDefinition) -> None:
        page = next(page for page in self.project.pages if page.page_id == page_id)
        self._upsert_by_attr(page.widgets, widget, "widget_id")

    def _upsert_by_attr(self, collection, value, attr_name: str) -> None:
        identifier = getattr(value, attr_name)
        for index, existing in enumerate(collection):
            if getattr(existing, attr_name) == identifier:
                collection[index] = value
                return
        collection.append(value)

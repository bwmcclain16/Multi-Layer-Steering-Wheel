from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from ..core.example_project import build_example_project
from ..core.models import DashboardProject
from ..core.project_io import load_project
from ..core.runtime import ActiveAlert, RuntimeContext


@dataclass
class DashSnapshot:
    page_name: str
    widgets: List[Dict[str, Any]]
    alerts: List[Dict[str, Any]]


class DashController:
    def __init__(self, project: DashboardProject | None = None) -> None:
        self.project = project or build_example_project()
        self.context = RuntimeContext(self.project)

    def load(self, path: str | Path) -> DashboardProject:
        self.project = load_project(path)
        self.context = RuntimeContext(self.project)
        return self.project

    def tick(self) -> DashSnapshot:
        active_alerts = self.context.tick()
        page = self.context.current_page
        widgets = []
        if page:
            for widget in page.widgets:
                state = self.context.store.states[widget.signal_id]
                widgets.append(
                    {
                        "widget_id": widget.widget_id,
                        "name": widget.name,
                        "signal_id": widget.signal_id,
                        "formatted_value": state.formatted_value(),
                        "stale": state.stale,
                        "widget_type": widget.widget_type.value,
                    }
                )
        return DashSnapshot(
            page_name=page.name if page else "No Page",
            widgets=widgets,
            alerts=[alert.__dict__ for alert in active_alerts],
        )

    def next_page(self) -> None:
        self.context.next_page()

    def headless_run(self, ticks: int = 3) -> List[DashSnapshot]:
        return [self.tick() for _ in range(ticks)]

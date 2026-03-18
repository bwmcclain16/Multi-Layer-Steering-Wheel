from __future__ import annotations

import json
from pathlib import Path

from .models import DashboardProject


def load_project(path: str | Path) -> DashboardProject:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return DashboardProject.from_dict(payload)


def save_project(project: DashboardProject, path: str | Path) -> None:
    Path(path).write_text(json.dumps(project.to_dict(), indent=2, sort_keys=True), encoding="utf-8")

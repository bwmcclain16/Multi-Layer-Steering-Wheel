# Architecture Overview

## Product shape

The platform is intentionally split into two user-facing applications:

1. **Editor application** (`motorsport_dashboard_platform.editor.app`) for visually creating and editing dashboard projects.
2. **Dash application** (`motorsport_dashboard_platform.dash.app`) for previewing and running a dashboard against normalized live signals.

Both applications share the same Python package foundation under `src/motorsport_dashboard_platform/`.

## Core layers

### Domain model

The domain layer centers on a `DashboardProject` aggregate that owns:

- metadata and assets
- normalized signals
- backend definitions
- CAN buses/messages/signals/mappings
- themes, widgets, pages, alerts, peripherals, hardware rules, and profiles

Every signal in the platform is represented by a **definition** (`SignalDefinition`) and a **runtime state** (`SignalState`). That split keeps source-specific telemetry separate from dashboard rendering and alert evaluation.

### Serialization and validation

`core.project_io` handles JSON persistence while `core.validation` enforces referential integrity and required design constraints. This makes the editor and the dash runtime use a common contract for project files.

### Runtime and rules

`core.runtime` provides:

- `SignalStore` for normalized signal updates, smoothing, deadband handling, timeout processing, and stale/missing state.
- `AlertEngine` for rules evaluation against normalized signals.
- `RuntimeContext` for runtime orchestration and future backend swapping.
- `MockTelemetryBackend` as the initial backend implementation.

### Editor architecture

The editor is a Tkinter multi-tab desktop application with:

- list/detail editing for signals, pages, widgets, alerts, and profiles
- metadata editing form
- JSON inspection/export tab
- validation tab
- page canvas preview on the widgets tab

The `EditorController` owns mutations, persistence, and validation so the UI stays thin and testable.

### Dash runtime architecture

The dash runtime uses `DashController` and `RuntimeContext` to:

- load a project
- poll normalized telemetry data from a backend
- tick the signal store
- evaluate alerts
- render the current page
- support headless mode for automated tests and CI smoke runs

## Extensibility roadmap

The scaffold explicitly reserves space for:

- real CAN bus adapters and DBC importers
- sim telemetry adapters (iRacing, ACC, rFactor, etc.)
- derived signal expressions
- richer widget registry and renderer abstractions
- peripheral output drivers and output-rule execution
- configuration migrations and profile overlays

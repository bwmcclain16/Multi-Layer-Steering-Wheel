# Multi-Layer Steering Wheel / Motorsport Dashboard Platform

A Python-first, reusable motorsport telemetry dashboard platform scaffold for sim racing, real vehicles, FSAE dashboards, and future custom display projects.

## What this repository provides

- a unified normalized signal model
- a visual multi-tab **Editor** desktop application
- a reusable **Dash** runtime desktop application with headless mode
- configuration-driven signals, widgets, pages, themes, profiles, alerts, CAN mappings, and peripherals
- project JSON serialization and validation
- a runtime signal store with stale/missing handling, smoothing, and deadband behavior
- a starter alert engine and mock telemetry backend
- example project configuration spanning sim signals and FSAE/CAN-style signals
- direct launchers under `bin/`
- tests and architecture documentation

## Repository layout

- `src/motorsport_dashboard_platform/` — shared package and both applications
- `src/motorsport_dashboard_platform/core/` — domain models, validation, project IO, runtime, example project
- `src/motorsport_dashboard_platform/editor/` — editor controller and Tkinter visual editor
- `src/motorsport_dashboard_platform/dash/` — dash controller and Tkinter runtime app
- `src/motorsport_dashboard_platform/examples/demo_project.json` — example project file
- `docs/architecture/overview.md` — architecture overview and extension points
- `bin/` — POSIX and Windows launchers
- `tests/` — unit and smoke tests

## Architecture summary

The platform is built around a `DashboardProject` aggregate that stores all configuration. Runtime telemetry never binds widgets directly to source-specific fields; widgets bind to normalized platform signal IDs. The runtime keeps definitions (`SignalDefinition`) separate from live state (`SignalState`) and evaluates alerts against the normalized store.

The code intentionally separates:

- **Editor app** — build/edit/validate dashboard projects visually
- **Dash app** — run/preview pages with live or future live-like backends
- **Core package** — shared contracts, runtime logic, persistence, and validation

## Quick start

### Run the editor

```bash
./bin/mlsw-editor
```

### Run the dash preview

```bash
./bin/mlsw-dash
```

### Headless validation/export

```bash
./bin/mlsw-editor --headless --validate
./bin/mlsw-editor --headless --export-json
```

### Headless runtime preview

```bash
./bin/mlsw-dash --headless --ticks 3
```

### Run tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Example project contents

The included example project demonstrates:

- sim-style normalized signals: RPM, gear, speed
- FSAE/CAN-style signals: battery voltage, CAN bus health
- a starter dashboard page with multiple widgets
- a theme definition
- alert definitions
- a profile definition
- a peripheral plus a hardware rule
- CAN bus, message, signal, and mapping scaffolding

## Packaging

The repo includes `pyproject.toml` with console scripts:

- `mlsw-editor`
- `mlsw-dash`

## Notes

- The editor uses Tkinter forms and list/detail editing instead of being a raw JSON editor.
- The dash supports headless execution for tests and can later be connected to real telemetry backends.
- CAN, sim, and peripheral integrations are scaffolded at the model/runtime boundary for future implementation.

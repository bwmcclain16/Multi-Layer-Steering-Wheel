# Multi-Layer Steering Wheel / Motorsport Dashboard Platform

A greenfield, Python-first motorsport dashboard platform intended to support:

- sim racing dashboards
- real vehicle dashboards
- FSAE dashboards
- future custom telemetry and HMI display projects

## Platform goals

- unified signal-driven architecture
- rich editor separated from lightweight runtime
- reusable widget/page/theme/profile system
- first-class CAN support for FSAE and real vehicle use
- future-proof backend and peripheral extensibility
- robust stale/missing data handling
- configurable alerts, styles, and hardware outputs

## Repository structure

- `docs/architecture/` — architecture and roadmap documents
- `apps/dash/` — runnable Python dashboard application
- `apps/editor/` — runnable Python editor application
- `src/motorsport_dashboard_platform/` — shared Python domain models, validation, IO, runtime signal logic, rules, and CLI tools
- `tests/` — foundational unit tests for schemas, validation, and runtime behavior

## Current status

This repository now contains:

- architecture documentation
- Python domain/configuration models
- project serialization and validation utilities
- runtime signal store and alert evaluation foundations
- a comprehensive example project definition
- CLI entry points for exporting and validating project files
- two runnable applications: `mlsw-editor` and `mlsw-dash`
- a multi-tab visual editor for metadata, signals, widgets, pages, alerts, profiles, and JSON export

## Quick start

```bash
./bin/mlsw-editor --headless --validate
./bin/mlsw-dash --headless --ticks 3
PYTHONPATH=src python -m unittest discover -s tests
```

## Recommended next build priorities

1. JSON schema export/import and migrations
2. concrete backend adapters (iRacing hub, CAN, UDP, serial)
3. runtime rendering layer and widget registry
4. editor application and property inspector flows
5. peripheral drivers and deployment packaging


## Direct launchers

Two executable launchers are included in-repo so you can run the apps directly without packaging first:

- `./bin/mlsw-editor` / `bin\mlsw-editor.bat`
- `./bin/mlsw-dash` / `bin\mlsw-dash.bat`

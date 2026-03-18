# Phased Roadmap

## Phase 0 — Foundation
- architecture documents
- domain model
- shared contracts/schema package
- example project definition
- repo scaffold

## Phase 1 — Minimal Vertical Slice
- signal store core
- mock backend
- derived signal support
- basic rules/alert engine
- runtime shell
- minimal widgets: numeric, gear, rpm bar, status indicator
- preview with fake data

## Phase 2 — Editor MVP
- page canvas
- widget palette
- property inspector
- signal browser
- page/profile/theme management
- preview mode
- project save/load

## Phase 3 — Sim Racing Path
- Windows telemetry hub
- iRacing adapter
- normalized stream protocol between hub and runtime
- Raspberry Pi deployment target
- shift light peripheral support
- GT3/hypercar sample profiles

## Phase 4 — Robustness and Diagnostics
- stale/missing handling improvements
- diagnostics pages
- replay/logging foundation
- acknowledgment/latching alert flows
- health/status signals

## Phase 5 — CAN / FSAE Core
- CAN backend
- manual CAN decode config
- message and bus timeout monitoring
- FSAE profile and example pages
- CAN-specific alerting and degraded-state behavior

## Phase 6 — Advanced Authoring and Packaging
- alignment/distribution tools
- widget templates/composites
- import/export packaging
- deployment tooling
- advanced theme editor

## Phase 7 — Platform Expansion
- DBC import support
- more simulator adapters
- touch and hardware inputs
- remote configuration
- custom widget plugin system
- advanced peripheral integrations

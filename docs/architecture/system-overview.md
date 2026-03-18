# System Overview

## Product framing

The platform is designed as a configurable, signal-driven HMI and dashboard product rather than a one-off sim dashboard.

It is intended to support:

- simulator telemetry dashboards
- CAN-based real vehicle dashboards
- FSAE instrument clusters and HMIs
- future telemetry display and peripheral control projects

## Major subsystems

### 1. Project Model and Configuration Core
Holds the source-of-truth document model used by both the editor and the runtime package compiler.

Responsibilities:
- project, profile, page, widget, theme, signal, alert, backend, and hardware schemas
- import/export and packaging
- validation and future migration/versioning

### 2. Signal Platform
Transforms all telemetry into normalized internal signals.

Responsibilities:
- backend ingestion handoff
- signal normalization
- signal freshness and timeout tracking
- smoothing, formatting, validation, and fallback behavior
- derived/computed signal generation

### 3. Backend Adapter Layer
Provides source-specific adapters that feed the signal platform.

Initial/future adapters:
- iRacing telemetry hub
- CAN
- UDP
- WebSocket
- serial
- mock data
- replay/log sources

### 4. Rules and Alert Engine
Evaluates conditions against normalized signals and produces active alert state.

Responsibilities:
- thresholds, ranges, and boolean conditions
- latching and acknowledgment behavior
- priority ordering
- page/global alert presentation state
- future hardware or action outputs

### 5. Rendering Runtime
Loads compiled project packages and renders pages/widgets efficiently.

Responsibilities:
- widget instantiation and binding
- page switching
- style and theme application
- alert overlays and degraded-state behavior
- runtime-safe handling of stale or missing signals

### 6. Hardware and Peripheral Runtime
Controls external outputs and future input devices.

Examples:
- shift LEDs
- warning LEDs
- external indicator bars
- buttons
- touch inputs
- future ESP or controller devices

### 7. Editor Application
A richer authoring environment intended for PC usage.

Responsibilities:
- page layout and drag/drop editing
- signal binding browser
- alert editor
- theme editor
- profile manager
- CAN mapping UI
- preview and simulation modes

## Deployment topologies

### Hub + Display Client
Best for simulator use cases.

- Windows PC hub ingests simulator telemetry
- hub normalizes or forwards telemetry
- Raspberry Pi runtime renders the display
- peripherals can live on either the hub or the runtime node

### Local Embedded Runtime
Best for CAN/FSAE use cases.

- runtime node reads CAN locally
- runtime decodes and normalizes signals
- runtime renders display and drives peripherals locally

## Core design principles

- treat all live values as normalized signals
- keep editor and runtime as separate applications
- avoid coupling widgets to any particular backend
- make CAN first-class from day one
- model stale/missing/degraded data explicitly
- keep styling and alerts data-driven
- support multiple profiles and deployment contexts without forking code

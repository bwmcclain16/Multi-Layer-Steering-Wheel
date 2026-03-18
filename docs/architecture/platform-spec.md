# Platform Specification

## Purpose

This document captures the initial product architecture for a modular, configurable motorsport dashboard platform.

The platform is intended to support:
- sim racing dashboards
- real vehicle dashboards
- FSAE dashboards
- future custom telemetry display and peripheral projects

## Architectural stance

The platform is centered around four ideas:

1. normalized signals are the universal runtime data contract
2. the editor and runtime are separate applications
3. configuration and schemas are first-class product features
4. backend and peripheral integrations are adapters, not assumptions

## Editor vs runtime separation

### Editor
Optimized for authoring richness.

Capabilities:
- drag/drop page editing
- alignment, snapping, and layering tools
- property inspectors
- signal browser and binding workflow
- theme editor
- alert/rule editor
- CAN signal mapping editor
- preview and mock-data simulation
- import/export/package workflows

### Runtime
Optimized for reliability and low overhead.

Capabilities:
- load compiled project package
- bind widgets to normalized signals
- render efficiently on Raspberry Pi or PC
- evaluate alerts and show overlays
- drive configured peripherals
- degrade safely on stale/missing data

### Shared contracts
Both applications should share:
- project schema
- signal contracts
- alert contracts
- widget manifests/contracts
- backend/peripheral contracts
- project compiler output format

## Unified signal model

A signal should be represented through three layers:

### Signal definition
Describes what the signal means.

Examples:
- `vehicle.engine.rpm`
- `vehicle.transmission.gear`
- `vehicle.speed`
- `session.lap.delta`
- `vehicle.battery.voltage`
- `system.can.bus0.health`

### Signal mapping
Describes how the signal is produced from a backend or formula.

Examples:
- iRacing field -> normalized signal
- CAN decoded field -> normalized signal
- derived formula -> normalized signal
- mock generator -> normalized signal

### Signal state
Describes the runtime value and health state.

Quality states:
- valid
- stale
- missing
- invalid
- substituted
- frozen

## Widget model

A widget instance should consist of:
- widget type id
- named signal bindings
- properties
- layout
- style ref and overrides
- visibility/state rules
- stale/missing data behavior

### Widget design principles
- widgets bind to normalized signals only
- widgets do not know backend specifics
- widgets should support theme-driven defaults
- composite widgets should be supported later
- widget metadata should be schema-driven for editor inspectors

## Layout model

Recommended approach:
- fixed reference canvas per page
- absolute placement for precision
- anchor rules for adaptation
- optional safe areas
- scale-to-fit runtime strategy
- editor grid/snapping/alignment tooling

Why this model:
- dashboard HMIs are precision layouts
- visual composition matters more than free-flow responsiveness
- supports 5–7 inch sim displays and future aspect variants
- fits both side-mounted screens and embedded vehicle displays

## Theme and styling model

Use token-based theming rather than scattered widget-local styles.

Theme layers:
1. global theme tokens
2. widget defaults
3. page-level overrides
4. widget instance overrides
5. conditional state overrides

Token types:
- colors
- fonts
- spacing
- radii
- borders
- opacity
- semantic severity/status tokens

## Alert and rules engine

Alerts are stateful evaluators over normalized signal state.

Capabilities:
- thresholds, ranges, booleans, and combined logic
- activation and clear delays
- latching and acknowledgment
- priorities and severities
- global or page-scoped presentation
- future output actions for hardware/peripherals

Examples:
- low battery voltage
- CAN timeout
- stale telemetry
- coolant temperature too high
- pit limiter active
- fault state active

## CAN strategy

CAN should flow through:
- raw frame ingestion
- message timeout tracking
- decode layer
- CAN-to-signal mapping layer
- normalized signal store

Configuration should eventually support:
- bus definitions
- message definitions
- bit extraction layout
- endianness
- signed/unsigned
- scale and offset
- units
- timeout behavior
- enum maps
- alert linkage

DBC support should be added later as an import path into the same internal schema.

## Peripheral strategy

Peripherals should be controlled through logical outputs and rules.

Examples:
- shift bar follows engine RPM
- warning LED flashes on critical alerts
- pit indicator lights when limiter active

Important design choice:
- logical outputs should be mapped to physical devices per profile or hardware setup
- display widgets should not directly own peripheral logic

## Deployment modes

### Simulator deployment
- Windows hub for iRacing/simulator SDKs
- normalized telemetry sent to Raspberry Pi runtime
- optional PC-side peripheral support

### Vehicle deployment
- local runtime on Pi or embedded Linux target
- local CAN ingestion and alerting
- local display and peripheral control

## Maintainability rules

- never couple widgets to source-specific fields
- never put business logic inside display components when it belongs in rules
- version schemas explicitly
- support project migrations over time
- treat system health as first-class signals
- keep editor-only metadata out of runtime packages

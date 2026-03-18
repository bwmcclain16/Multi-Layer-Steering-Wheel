# Domain Model Proposal

## Core entities

### Project
Top-level authoring and deployment container.

Contains:
- metadata
- assets
- signal definitions
- backend definitions
- CAN definitions
- themes
- widget presets/templates
- profiles
- deployment settings

### Profile
A use-case-specific configuration slice.

Examples:
- GT3 sim profile
- Hypercar sim profile
- FSAE profile
- testing/debug profile

Contains:
- active backends
- signal mappings
- page set
- default page
- theme selection/overrides
- alert set
- hardware mapping
- unit preferences

### Page
A dashboard canvas or overlay.

Contains:
- reference resolution
- background and overlays
- widget composition
- page-level style override
- page behavior and switching rules

### Widget
Reusable visual building block.

Structure:
- type
- properties
- signal bindings
- layout
- style refs/overrides
- visibility and state rules
- missing/stale data behavior

### Theme
Token-based styling system.

Contains:
- color tokens
- font tokens
- severity/status colors
- page styles
- widget defaults
- page/widget overrides

### Signal Definition
Stable meaning of a live value independent of source.

Recommended fields:
- id
- display name
- category
- data type
- units
- format rules
- expected range
- smoothing/deadband
- freshness policy
- fallback policy
- enum map
- aliases

### Signal Mapping
Connects a normalized signal id to a backend source.

Examples:
- iRacing field -> `vehicle.engine.rpm`
- CAN decoded signal -> `vehicle.battery.voltage`
- formula -> `system.telemetry.health`

### Signal State
Runtime-only state object.

Recommended fields:
- signal id
- raw value
- normalized value
- timestamp
- quality state
- last update age
- last valid value
- fallback/substitution flags

### Alert
Configurable rule-driven stateful notification.

Recommended fields:
- id
- name
- severity
- priority
- condition
- latch behavior
- ack behavior
- activation/clear delays
- style
- target presentation
- optional future output actions

### Backend Definition
Describes source adapters and their runtime configuration.

Examples:
- hub websocket source
- local CAN interface
- local UDP listener
- mock generator
- replay source

### Hardware Definition
Describes peripherals and logical output mappings.

Examples:
- shift light bar
- warning LED
- GPIO output bank
- button controller

## Signal quality states

Each signal should explicitly support:
- valid
- stale
- missing
- invalid
- substituted
- frozen

## Layout recommendation

Use a hybrid dashboard layout model:
- fixed reference canvas per page
- absolute placement for precision
- anchor rules for adaptation
- optional safe areas
- editor snapping/grid/alignment tools
- future aspect-ratio variants where needed

This is a better fit for motorsport HMIs than a purely responsive web layout model.

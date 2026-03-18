from __future__ import annotations

from .models import (
    AlertDefinition,
    AlertSeverity,
    BackendDefinition,
    BackendType,
    CanBusDefinition,
    CanMapping,
    CanMessageDefinition,
    CanSignalDefinition,
    DashboardPage,
    DashboardProfile,
    DashboardProject,
    HardwareRule,
    PeripheralDefinition,
    ProjectMetadata,
    SignalDefinition,
    SignalType,
    ThemeDefinition,
    WidgetDefinition,
    WidgetType,
)


def build_example_project() -> DashboardProject:
    return DashboardProject(
        metadata=ProjectMetadata(
            project_id="mlsw-demo",
            name="MLSW Demo Motorsport Project",
            description="Example project blending sim racing and FSAE CAN telemetry.",
            author="OpenAI Codex",
            tags=["sim", "fsae", "can", "demo"],
        ),
        assets={"logo": "assets/logo.png"},
        signals=[
            SignalDefinition("engine_rpm", "Engine RPM", "powertrain", SignalType.INTEGER, "rpm", "{value:.0f}", smoothing_factor=0.2, timeout_ms=500),
            SignalDefinition("vehicle_speed", "Vehicle Speed", "vehicle", SignalType.FLOAT, "mph", "{value:.1f}", smoothing_factor=0.1, timeout_ms=500),
            SignalDefinition("gear", "Gear", "powertrain", SignalType.ENUM, enum_mapping={"N": "Neutral", "1": "1", "2": "2", "3": "3", "4": "4", "5": "5", "6": "6"}, timeout_ms=800),
            SignalDefinition("battery_voltage", "Battery Voltage", "electrical", SignalType.FLOAT, "V", "{value:.2f}", timeout_ms=1000, fallback_value=0.0),
            SignalDefinition("can_bus_health", "CAN Bus Health", "network", SignalType.INTEGER, "%", "{value:.0f}", timeout_ms=1000, fallback_value=0),
        ],
        backends=[
            BackendDefinition(
                backend_id="mock-primary",
                name="Mock Telemetry",
                backend_type=BackendType.MOCK,
                settings={"tick_ms": 250},
                signal_map={
                    "rpm": "engine_rpm",
                    "speed": "vehicle_speed",
                    "gear": "gear",
                },
            )
        ],
        can_buses=[CanBusDefinition("vehicle_can", "Vehicle CAN", "can0", 500000, "Primary FSAE telemetry bus")],
        can_messages=[CanMessageDefinition("bms_status", "vehicle_can", 0x301, 8, 20, "Battery management system status")],
        can_signals=[
            CanSignalDefinition("bms_pack_voltage_raw", "bms_status", 0, 16, "little_endian", False, 0.1, 0.0, 0.0, 600.0, "V", 100, "Pack voltage from BMS"),
            CanSignalDefinition("vehicle_can_health_raw", "bms_status", 16, 8, "little_endian", False, 1.0, 0.0, 0.0, 100.0, "%", 100, "Percent CAN bus health"),
        ],
        can_mappings=[
            CanMapping("bms_pack_voltage_raw", "battery_voltage", None),
            CanMapping("vehicle_can_health_raw", "can_bus_health", None),
        ],
        themes=[
            ThemeDefinition(
                theme_id="night-race",
                name="Night Race",
                palette={
                    "background": "#08111f",
                    "foreground": "#f2f7ff",
                    "accent": "#ff5c39",
                    "warning": "#ffc857",
                    "critical": "#ff3864",
                },
                font_family="TkDefaultFont",
                font_size=12,
                widget_style_defaults={"padding": 8},
            )
        ],
        pages=[
            DashboardPage(
                page_id="race-main",
                name="Race Main",
                theme_id="night-race",
                widgets=[
                    WidgetDefinition("rpm-gauge", "RPM", WidgetType.GAUGE, "engine_rpm", 20, 20, 180, 120, {"max": 9000}),
                    WidgetDefinition("speed-text", "Speed", WidgetType.TEXT, "vehicle_speed", 220, 20, 140, 80, {}),
                    WidgetDefinition("gear-indicator", "Gear", WidgetType.INDICATOR, "gear", 220, 120, 140, 80, {}),
                    WidgetDefinition("battery-bar", "Battery", WidgetType.BAR, "battery_voltage", 20, 160, 200, 80, {"min": 250, "max": 400}),
                    WidgetDefinition("can-status", "CAN", WidgetType.STATUS, "can_bus_health", 240, 220, 140, 60, {}),
                ],
                background="#08111f",
                grid_size=20,
            )
        ],
        alerts=[
            AlertDefinition("rpm-high", "High RPM", "engine_rpm", ">=", 7800, AlertSeverity.WARNING, "RPM high: {value:.0f}", cooldown_ms=500),
            AlertDefinition("battery-low", "Battery Low", "battery_voltage", "<=", 300.0, AlertSeverity.CRITICAL, "Battery voltage low: {value:.2f}V", sticky=True),
        ],
        peripherals=[
            PeripheralDefinition("shift-light-bar", "Shift Light Bar", "led_strip", {"port": "COM4", "pixels": 8}),
        ],
        hardware_rules=[
            HardwareRule("shift-warning", "Blink shift lights on high RPM", "shift-light-bar", trigger_alert_id="rpm-high", output_action="blink", settings={"color": "#ff5c39", "pattern": "fast"}),
        ],
        profiles=[
            DashboardProfile("sim-driver", "Sim Driver", ["race-main"], "race-main", ["mock-primary"], {"brightness": 0.8}),
        ],
    )

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import (
    AlertDefinition,
    AlertScope,
    AlertSeverity,
    AssetDefinition,
    BackgroundDefinition,
    BackendDefinition,
    BackendType,
    CanBusDefinition,
    CanMessageDefinition,
    CanMode,
    CanSignalDecodeDefinition,
    DashboardProject,
    Endianness,
    FallbackMode,
    HardwareRuleDefinition,
    LatchBehavior,
    LayoutAnchor,
    NumericRange,
    PageDefinition,
    PageType,
    PeripheralDefinition,
    PeripheralType,
    ProfileDefinition,
    ProjectMetadata,
    Resolution,
    SafeArea,
    SignalDataType,
    SignalDefinition,
    SignalFallbackPolicy,
    SignalFormatting,
    SignalFreshnessPolicy,
    SignalMapping,
    SignalSmoothing,
    SmoothingMode,
    ThemeDefinition,
    ThemeTokenSet,
    TransformStep,
    TransformType,
    WidgetBinding,
    WidgetDataBehavior,
    WidgetDataStateBehavior,
    WidgetDefinition,
    WidgetLayout,
)


def save_project(project: DashboardProject, path: str | Path, *, pretty: bool = True) -> None:
    path = Path(path)
    payload = project.to_dict()
    if pretty:
        path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    else:
        path.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")


def load_project(path: str | Path) -> DashboardProject:
    return project_from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def project_from_dict(payload: dict[str, Any]) -> DashboardProject:
    return DashboardProject(
        metadata=ProjectMetadata(
            id=payload["metadata"]["id"],
            name=payload["metadata"]["name"],
            version=payload["metadata"]["version"],
            schema_version=payload["metadata"]["schema_version"],
            description=payload["metadata"].get("description"),
            author=payload["metadata"].get("author"),
            created_at_iso=payload["metadata"].get("created_at_iso"),
            updated_at_iso=payload["metadata"].get("updated_at_iso"),
        ),
        assets=[AssetDefinition(**asset) for asset in payload.get("assets", [])],
        signals=[_signal_definition(item) for item in payload.get("signals", [])],
        backends=[_backend_definition(item) for item in payload.get("backends", [])],
        can_buses=[_can_bus(item) for item in payload.get("can_buses", [])],
        can_messages=[CanMessageDefinition(**item) for item in payload.get("can_messages", [])],
        can_signals=[_can_signal(item) for item in payload.get("can_signals", [])],
        mappings=[_signal_mapping(item) for item in payload.get("mappings", [])],
        themes=[_theme_definition(item) for item in payload.get("themes", [])],
        widgets=[_widget_definition(item) for item in payload.get("widgets", [])],
        pages=[_page_definition(item) for item in payload.get("pages", [])],
        alerts=[_alert_definition(item) for item in payload.get("alerts", [])],
        peripherals=[_peripheral_definition(item) for item in payload.get("peripherals", [])],
        hardware_rules=[HardwareRuleDefinition(**item) for item in payload.get("hardware_rules", [])],
        profiles=[ProfileDefinition(**item) for item in payload.get("profiles", [])],
    )


def _signal_definition(item: dict[str, Any]) -> SignalDefinition:
    return SignalDefinition(
        id=item["id"],
        display_name=item["display_name"],
        category=item["category"],
        data_type=SignalDataType(item["data_type"]),
        units=item.get("units"),
        description=item.get("description"),
        aliases=item.get("aliases", []),
        expected_range=NumericRange(**item["expected_range"]) if item.get("expected_range") else None,
        formatting=SignalFormatting(**item["formatting"]) if item.get("formatting") else None,
        freshness=SignalFreshnessPolicy(**item["freshness"]) if item.get("freshness") else None,
        fallback=_signal_fallback(item.get("fallback")),
        smoothing=_signal_smoothing(item.get("smoothing")),
        deadband=item.get("deadband"),
        enum_map=item.get("enum_map", {}),
        tags=item.get("tags", []),
    )


def _signal_fallback(item: dict[str, Any] | None) -> SignalFallbackPolicy | None:
    if item is None:
        return None
    return SignalFallbackPolicy(mode=FallbackMode(item["mode"]), default_value=item.get("default_value"))


def _signal_smoothing(item: dict[str, Any] | None) -> SignalSmoothing | None:
    if item is None:
        return None
    return SignalSmoothing(
        mode=SmoothingMode(item.get("mode", SmoothingMode.NONE)),
        alpha=item.get("alpha"),
        window_size=item.get("window_size"),
    )


def _backend_definition(item: dict[str, Any]) -> BackendDefinition:
    return BackendDefinition(
        id=item["id"],
        type=BackendType(item["type"]),
        name=item["name"],
        config=item.get("config", {}),
        enabled_by_default=item.get("enabled_by_default", True),
    )


def _can_bus(item: dict[str, Any]) -> CanBusDefinition:
    return CanBusDefinition(
        id=item["id"],
        interface_name=item["interface_name"],
        bitrate=item["bitrate"],
        mode=CanMode(item.get("mode", CanMode.CLASSIC)),
        listen_only=item.get("listen_only", False),
        health_timeout_ms=item.get("health_timeout_ms"),
    )


def _can_signal(item: dict[str, Any]) -> CanSignalDecodeDefinition:
    return CanSignalDecodeDefinition(
        id=item["id"],
        message_id=item["message_id"],
        name=item["name"],
        start_bit=item["start_bit"],
        bit_length=item["bit_length"],
        endianness=Endianness(item["endianness"]),
        signed=item["signed"],
        scale=item.get("scale", 1.0),
        offset=item.get("offset", 0.0),
        units=item.get("units"),
        expected_range=NumericRange(**item["expected_range"]) if item.get("expected_range") else None,
        enum_map=item.get("enum_map", {}),
    )


def _signal_mapping(item: dict[str, Any]) -> SignalMapping:
    return SignalMapping(
        id=item["id"],
        signal_id=item["signal_id"],
        backend_id=item["backend_id"],
        source_type=item["source_type"],
        source_ref=item["source_ref"],
        transforms=[TransformStep(type=TransformType(step["type"]), config=step.get("config", {})) for step in item.get("transforms", [])],
        freshness_override=SignalFreshnessPolicy(**item["freshness_override"]) if item.get("freshness_override") else None,
        enabled=item.get("enabled", True),
    )


def _theme_definition(item: dict[str, Any]) -> ThemeDefinition:
    return ThemeDefinition(
        id=item["id"],
        name=item["name"],
        tokens=ThemeTokenSet(**item.get("tokens", {})),
        widget_defaults=item.get("widget_defaults", {}),
        page_defaults=item.get("page_defaults", {}),
    )


def _widget_definition(item: dict[str, Any]) -> WidgetDefinition:
    return WidgetDefinition(
        id=item["id"],
        type=item["type"],
        name=item["name"],
        layout=WidgetLayout(
            x=item["layout"]["x"],
            y=item["layout"]["y"],
            width=item["layout"]["width"],
            height=item["layout"]["height"],
            anchor=LayoutAnchor(item["layout"].get("anchor", LayoutAnchor.TOP_LEFT)),
            z_index=item["layout"].get("z_index", 0),
            rotation_deg=item["layout"].get("rotation_deg", 0.0),
        ),
        bindings=[WidgetBinding(**binding) for binding in item.get("bindings", [])],
        props=item.get("props", {}),
        style_ref=item.get("style_ref"),
        style_overrides=item.get("style_overrides", {}),
        state_styles=item.get("state_styles", {}),
        visibility_rule=item.get("visibility_rule"),
        data_behavior=_widget_data_behavior(item.get("data_behavior")),
        enabled=item.get("enabled", True),
    )


def _widget_data_behavior(item: dict[str, Any] | None) -> WidgetDataBehavior | None:
    if item is None:
        return None
    return WidgetDataBehavior(
        on_stale=WidgetDataStateBehavior(item.get("on_stale", WidgetDataStateBehavior.SHOW)),
        on_missing=WidgetDataStateBehavior(item.get("on_missing", WidgetDataStateBehavior.SHOW)),
        placeholder_text=item.get("placeholder_text"),
    )


def _page_definition(item: dict[str, Any]) -> PageDefinition:
    return PageDefinition(
        id=item["id"],
        name=item["name"],
        reference_resolution=Resolution(**item["reference_resolution"]),
        type=PageType(item.get("type", PageType.DASHBOARD)),
        background=BackgroundDefinition(**item["background"]) if item.get("background") else None,
        theme_override_id=item.get("theme_override_id"),
        widget_ids=item.get("widget_ids", []),
        safe_area=SafeArea(**item["safe_area"]) if item.get("safe_area") else None,
        page_switch_rules=item.get("page_switch_rules", []),
    )


def _alert_definition(item: dict[str, Any]) -> AlertDefinition:
    return AlertDefinition(
        id=item["id"],
        name=item["name"],
        description=item.get("description"),
        severity=AlertSeverity(item["severity"]),
        priority=item["priority"],
        enabled=item.get("enabled", True),
        scope=AlertScope(item["scope"]),
        condition=item["condition"],
        latch_behavior=LatchBehavior(item.get("latch_behavior", LatchBehavior.NONE)),
        acknowledgment_required=item.get("acknowledgment_required", False),
        activation_delay_ms=item.get("activation_delay_ms", 0),
        clear_delay_ms=item.get("clear_delay_ms", 0),
        style_ref=item.get("style_ref"),
        target_pages=item.get("target_pages", []),
        output_targets=item.get("output_targets", []),
    )


def _peripheral_definition(item: dict[str, Any]) -> PeripheralDefinition:
    return PeripheralDefinition(
        id=item["id"],
        type=PeripheralType(item["type"]),
        name=item["name"],
        config=item.get("config", {}),
    )

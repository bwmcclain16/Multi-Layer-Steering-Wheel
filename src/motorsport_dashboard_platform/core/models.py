from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields, is_dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class SignalType(str, Enum):
    FLOAT = "float"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    STRING = "string"
    ENUM = "enum"


class WidgetType(str, Enum):
    GAUGE = "gauge"
    BAR = "bar"
    TEXT = "text"
    INDICATOR = "indicator"
    STATUS = "status"


class BackendType(str, Enum):
    MOCK = "mock"
    CAN = "can"
    SIM = "sim"
    UDP = "udp"
    SERIAL = "serial"


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class ProjectMetadata:
    project_id: str
    name: str
    description: str = ""
    version: str = "0.1.0"
    author: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class SignalDefinition:
    signal_id: str
    display_name: str
    category: str
    signal_type: SignalType
    units: str = ""
    format_string: str = "{value}"
    smoothing_factor: float = 0.0
    deadband: float = 0.0
    timeout_ms: int = 1000
    fallback_value: Optional[Any] = None
    enum_mapping: Dict[str, str] = field(default_factory=dict)
    aliases: List[str] = field(default_factory=list)
    description: str = ""
    computed_expression: Optional[str] = None


@dataclass
class BackendDefinition:
    backend_id: str
    name: str
    backend_type: BackendType
    enabled: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)
    signal_map: Dict[str, str] = field(default_factory=dict)


@dataclass
class CanBusDefinition:
    bus_id: str
    name: str
    channel: str
    bitrate: int
    description: str = ""


@dataclass
class CanMessageDefinition:
    message_id: str
    bus_id: str
    arbitration_id: int
    length: int
    cycle_time_ms: int
    description: str = ""


@dataclass
class CanSignalDefinition:
    signal_id: str
    message_id: str
    start_bit: int
    bit_length: int
    byte_order: str
    signed: bool
    scale: float
    offset: float
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    units: str = ""
    timeout_ms: int = 500
    description: str = ""


@dataclass
class CanMapping:
    can_signal_id: str
    normalized_signal_id: str
    transform: Optional[str] = None


@dataclass
class ThemeDefinition:
    theme_id: str
    name: str
    palette: Dict[str, str] = field(default_factory=dict)
    font_family: str = "TkDefaultFont"
    font_size: int = 12
    widget_style_defaults: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WidgetDefinition:
    widget_id: str
    name: str
    widget_type: WidgetType
    signal_id: str
    x: int
    y: int
    width: int
    height: int
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DashboardPage:
    page_id: str
    name: str
    theme_id: str
    widgets: List[WidgetDefinition] = field(default_factory=list)
    background: str = "#101820"
    grid_size: int = 20


@dataclass
class AlertDefinition:
    alert_id: str
    name: str
    signal_id: str
    operator: str
    threshold: Any
    severity: AlertSeverity
    message: str
    sticky: bool = False
    cooldown_ms: int = 0


@dataclass
class PeripheralDefinition:
    peripheral_id: str
    name: str
    peripheral_type: str
    settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HardwareRule:
    rule_id: str
    name: str
    peripheral_id: str
    trigger_alert_id: Optional[str] = None
    output_action: str = ""
    settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DashboardProfile:
    profile_id: str
    name: str
    page_ids: List[str] = field(default_factory=list)
    default_page_id: str = ""
    enabled_backend_ids: List[str] = field(default_factory=list)
    theme_overrides: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DashboardProject:
    metadata: ProjectMetadata
    assets: Dict[str, str] = field(default_factory=dict)
    signals: List[SignalDefinition] = field(default_factory=list)
    backends: List[BackendDefinition] = field(default_factory=list)
    can_buses: List[CanBusDefinition] = field(default_factory=list)
    can_messages: List[CanMessageDefinition] = field(default_factory=list)
    can_signals: List[CanSignalDefinition] = field(default_factory=list)
    can_mappings: List[CanMapping] = field(default_factory=list)
    themes: List[ThemeDefinition] = field(default_factory=list)
    pages: List[DashboardPage] = field(default_factory=list)
    alerts: List[AlertDefinition] = field(default_factory=list)
    peripherals: List[PeripheralDefinition] = field(default_factory=list)
    hardware_rules: List[HardwareRule] = field(default_factory=list)
    profiles: List[DashboardProfile] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return _enum_safe(asdict(self))

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "DashboardProject":
        return cls(
            metadata=_from_dict(ProjectMetadata, payload["metadata"]),
            assets=payload.get("assets", {}),
            signals=[_from_dict(SignalDefinition, item) for item in payload.get("signals", [])],
            backends=[_from_dict(BackendDefinition, item) for item in payload.get("backends", [])],
            can_buses=[_from_dict(CanBusDefinition, item) for item in payload.get("can_buses", [])],
            can_messages=[_from_dict(CanMessageDefinition, item) for item in payload.get("can_messages", [])],
            can_signals=[_from_dict(CanSignalDefinition, item) for item in payload.get("can_signals", [])],
            can_mappings=[_from_dict(CanMapping, item) for item in payload.get("can_mappings", [])],
            themes=[_from_dict(ThemeDefinition, item) for item in payload.get("themes", [])],
            pages=[
                DashboardPage(
                    page_id=item["page_id"],
                    name=item["name"],
                    theme_id=item.get("theme_id", ""),
                    widgets=[_from_dict(WidgetDefinition, widget) for widget in item.get("widgets", [])],
                    background=item.get("background", "#101820"),
                    grid_size=item.get("grid_size", 20),
                )
                for item in payload.get("pages", [])
            ],
            alerts=[_from_dict(AlertDefinition, item) for item in payload.get("alerts", [])],
            peripherals=[_from_dict(PeripheralDefinition, item) for item in payload.get("peripherals", [])],
            hardware_rules=[_from_dict(HardwareRule, item) for item in payload.get("hardware_rules", [])],
            profiles=[_from_dict(DashboardProfile, item) for item in payload.get("profiles", [])],
        )


def _enum_safe(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: _enum_safe(inner) for key, inner in value.items()}
    if isinstance(value, list):
        return [_enum_safe(item) for item in value]
    return value


_TYPE_COERCIONS = {
    SignalType: SignalType,
    WidgetType: WidgetType,
    BackendType: BackendType,
    AlertSeverity: AlertSeverity,
}


def _from_dict(model_cls, payload: Dict[str, Any]):
    kwargs = {}
    for field_info in fields(model_cls):
        if field_info.name not in payload:
            continue
        value = payload[field_info.name]
        converter = _TYPE_COERCIONS.get(field_info.type)
        if converter is not None and value is not None:
            value = converter(value)
        kwargs[field_info.name] = value
    return model_cls(**kwargs)

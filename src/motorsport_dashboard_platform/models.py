from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from typing import Any


class StringEnum(str, Enum):
    def __str__(self) -> str:
        return str(self.value)


class SignalDataType(StringEnum):
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ENUM = "enum"
    STRING = "string"
    DURATION = "duration"
    PERCENTAGE = "percentage"
    BITFIELD = "bitfield"


class SignalQualityState(StringEnum):
    VALID = "valid"
    STALE = "stale"
    MISSING = "missing"
    INVALID = "invalid"
    SUBSTITUTED = "substituted"
    FROZEN = "frozen"


class AlertSeverity(StringEnum):
    INFO = "info"
    ADVISORY = "advisory"
    CAUTION = "caution"
    WARNING = "warning"
    CRITICAL = "critical"


class LayoutAnchor(StringEnum):
    TOP_LEFT = "top-left"
    TOP_CENTER = "top-center"
    TOP_RIGHT = "top-right"
    CENTER_LEFT = "center-left"
    CENTER = "center"
    CENTER_RIGHT = "center-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_CENTER = "bottom-center"
    BOTTOM_RIGHT = "bottom-right"


class FallbackMode(StringEnum):
    FREEZE_LAST = "freeze-last"
    DEFAULT_VALUE = "default-value"
    NULL = "null"
    HIDE = "hide"


class SmoothingMode(StringEnum):
    NONE = "none"
    EMA = "ema"
    MOVING_AVERAGE = "moving-average"


class BackendType(StringEnum):
    IRACING_HUB = "iracing-hub"
    CAN = "can"
    UDP = "udp"
    WEBSOCKET = "websocket"
    SERIAL = "serial"
    MOCK = "mock"
    REPLAY = "replay"
    CUSTOM = "custom"


class CanMode(StringEnum):
    CLASSIC = "classic"
    FD = "fd"


class Endianness(StringEnum):
    LITTLE = "little"
    BIG = "big"


class TransformType(StringEnum):
    SCALE = "scale"
    OFFSET = "offset"
    CLAMP = "clamp"
    MAP_ENUM = "map-enum"
    FORMULA = "formula"
    UNIT_CONVERT = "unit-convert"


class WidgetDataStateBehavior(StringEnum):
    SHOW = "show"
    GRAY_OUT = "gray-out"
    HIDE = "hide"
    FREEZE_LAST = "freeze-last"
    PLACEHOLDER = "placeholder"


class PageType(StringEnum):
    DASHBOARD = "dashboard"
    OVERLAY = "overlay"
    SPLASH = "splash"
    LOADING = "loading"
    DIAGNOSTICS = "diagnostics"


class AlertScope(StringEnum):
    GLOBAL = "global"
    PROFILE = "profile"
    PAGE = "page"


class LatchBehavior(StringEnum):
    NONE = "none"
    LATCHED_UNTIL_CLEAR = "latched-until-clear"
    LATCHED_UNTIL_ACK = "latched-until-ack"


class PeripheralType(StringEnum):
    SHIFT_LED_BAR = "shift-led-bar"
    INDICATOR_LIGHT = "indicator-light"
    GPIO = "gpio"
    SERIAL_DEVICE = "serial-device"
    TOUCH = "touch"
    BUTTON_INPUT = "button-input"
    CUSTOM = "custom"


@dataclass(slots=True)
class ProjectMetadata:
    id: str
    name: str
    version: str
    schema_version: str
    description: str | None = None
    author: str | None = None
    created_at_iso: str | None = None
    updated_at_iso: str | None = None


@dataclass(slots=True)
class NumericRange:
    min: float | None = None
    max: float | None = None


@dataclass(slots=True)
class SignalFormatting:
    decimals: int | None = None
    unit_display: str | None = None
    prefix: str | None = None
    suffix: str | None = None
    null_placeholder: str | None = None


@dataclass(slots=True)
class SignalFreshnessPolicy:
    stale_after_ms: int | None = None
    missing_after_ms: int | None = None
    invalid_on_timeout: bool = False


@dataclass(slots=True)
class SignalFallbackPolicy:
    mode: FallbackMode
    default_value: str | int | float | bool | None = None


@dataclass(slots=True)
class SignalSmoothing:
    mode: SmoothingMode = SmoothingMode.NONE
    alpha: float | None = None
    window_size: int | None = None


@dataclass(slots=True)
class SignalDefinition:
    id: str
    display_name: str
    category: str
    data_type: SignalDataType
    units: str | None = None
    description: str | None = None
    aliases: list[str] = field(default_factory=list)
    expected_range: NumericRange | None = None
    formatting: SignalFormatting | None = None
    freshness: SignalFreshnessPolicy | None = None
    fallback: SignalFallbackPolicy | None = None
    smoothing: SignalSmoothing | None = None
    deadband: float | None = None
    enum_map: dict[str, str] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class BackendDefinition:
    id: str
    type: BackendType
    name: str
    config: dict[str, Any] = field(default_factory=dict)
    enabled_by_default: bool = True


@dataclass(slots=True)
class CanBusDefinition:
    id: str
    interface_name: str
    bitrate: int
    mode: CanMode = CanMode.CLASSIC
    listen_only: bool = False
    health_timeout_ms: int | None = None


@dataclass(slots=True)
class CanMessageDefinition:
    id: str
    bus_id: str
    arbitration_id: str
    name: str
    expected_period_ms: int | None = None
    timeout_ms: int | None = None
    description: str | None = None


@dataclass(slots=True)
class CanSignalDecodeDefinition:
    id: str
    message_id: str
    name: str
    start_bit: int
    bit_length: int
    endianness: Endianness
    signed: bool
    scale: float = 1.0
    offset: float = 0.0
    units: str | None = None
    expected_range: NumericRange | None = None
    enum_map: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class TransformStep:
    type: TransformType
    config: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SignalMapping:
    id: str
    signal_id: str
    backend_id: str
    source_type: str
    source_ref: str
    transforms: list[TransformStep] = field(default_factory=list)
    freshness_override: SignalFreshnessPolicy | None = None
    enabled: bool = True


@dataclass(slots=True)
class ThemeTokenSet:
    colors: dict[str, str] = field(default_factory=dict)
    fonts: dict[str, str] = field(default_factory=dict)
    spacing: dict[str, int | float] = field(default_factory=dict)
    radii: dict[str, int | float] = field(default_factory=dict)
    borders: dict[str, int | float] = field(default_factory=dict)
    opacity: dict[str, int | float] = field(default_factory=dict)


@dataclass(slots=True)
class ThemeDefinition:
    id: str
    name: str
    tokens: ThemeTokenSet = field(default_factory=ThemeTokenSet)
    widget_defaults: dict[str, dict[str, Any]] = field(default_factory=dict)
    page_defaults: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WidgetLayout:
    x: int
    y: int
    width: int
    height: int
    anchor: LayoutAnchor = LayoutAnchor.TOP_LEFT
    z_index: int = 0
    rotation_deg: float = 0.0


@dataclass(slots=True)
class WidgetBinding:
    key: str
    signal_id: str


@dataclass(slots=True)
class WidgetDataBehavior:
    on_stale: WidgetDataStateBehavior = WidgetDataStateBehavior.SHOW
    on_missing: WidgetDataStateBehavior = WidgetDataStateBehavior.SHOW
    placeholder_text: str | None = None


@dataclass(slots=True)
class WidgetDefinition:
    id: str
    type: str
    name: str
    layout: WidgetLayout
    bindings: list[WidgetBinding] = field(default_factory=list)
    props: dict[str, Any] = field(default_factory=dict)
    style_ref: str | None = None
    style_overrides: dict[str, Any] = field(default_factory=dict)
    state_styles: dict[str, dict[str, Any]] = field(default_factory=dict)
    visibility_rule: str | None = None
    data_behavior: WidgetDataBehavior | None = None
    enabled: bool = True


@dataclass(slots=True)
class Resolution:
    width: int
    height: int


@dataclass(slots=True)
class SafeArea:
    top: int = 0
    right: int = 0
    bottom: int = 0
    left: int = 0


@dataclass(slots=True)
class BackgroundDefinition:
    color: str | None = None
    image_asset_id: str | None = None


@dataclass(slots=True)
class PageDefinition:
    id: str
    name: str
    reference_resolution: Resolution
    type: PageType = PageType.DASHBOARD
    background: BackgroundDefinition | None = None
    theme_override_id: str | None = None
    widget_ids: list[str] = field(default_factory=list)
    safe_area: SafeArea | None = None
    page_switch_rules: list[str] = field(default_factory=list)


@dataclass(slots=True)
class AlertDefinition:
    id: str
    name: str
    severity: AlertSeverity
    priority: int
    scope: AlertScope
    condition: str
    description: str | None = None
    enabled: bool = True
    latch_behavior: LatchBehavior = LatchBehavior.NONE
    acknowledgment_required: bool = False
    activation_delay_ms: int = 0
    clear_delay_ms: int = 0
    style_ref: str | None = None
    target_pages: list[str] = field(default_factory=list)
    output_targets: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PeripheralDefinition:
    id: str
    type: PeripheralType
    name: str
    config: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class HardwareRuleDefinition:
    id: str
    peripheral_id: str
    logical_output_id: str
    trigger: str
    action: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


@dataclass(slots=True)
class ProfileDefinition:
    id: str
    name: str
    backend_ids: list[str]
    mapping_ids: list[str]
    page_ids: list[str]
    default_page_id: str
    theme_id: str
    alert_ids: list[str] = field(default_factory=list)
    peripheral_ids: list[str] = field(default_factory=list)
    hardware_rule_ids: list[str] = field(default_factory=list)
    description: str | None = None
    unit_system: str = "metric"
    tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class AssetDefinition:
    id: str
    type: str
    path: str
    description: str | None = None


@dataclass(slots=True)
class DashboardProject:
    metadata: ProjectMetadata
    assets: list[AssetDefinition] = field(default_factory=list)
    signals: list[SignalDefinition] = field(default_factory=list)
    backends: list[BackendDefinition] = field(default_factory=list)
    can_buses: list[CanBusDefinition] = field(default_factory=list)
    can_messages: list[CanMessageDefinition] = field(default_factory=list)
    can_signals: list[CanSignalDecodeDefinition] = field(default_factory=list)
    mappings: list[SignalMapping] = field(default_factory=list)
    themes: list[ThemeDefinition] = field(default_factory=list)
    widgets: list[WidgetDefinition] = field(default_factory=list)
    pages: list[PageDefinition] = field(default_factory=list)
    alerts: list[AlertDefinition] = field(default_factory=list)
    peripherals: list[PeripheralDefinition] = field(default_factory=list)
    hardware_rules: list[HardwareRuleDefinition] = field(default_factory=list)
    profiles: list[ProfileDefinition] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _convert_to_primitive(asdict(self))


def _convert_to_primitive(value: Any) -> Any:
    if isinstance(value, Enum):
        return str(value)
    if is_dataclass(value):
        return _convert_to_primitive(asdict(value))
    if isinstance(value, dict):
        return {key: _convert_to_primitive(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_convert_to_primitive(item) for item in value]
    return value

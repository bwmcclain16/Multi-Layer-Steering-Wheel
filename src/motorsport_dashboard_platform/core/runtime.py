from __future__ import annotations

import itertools
import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

from .models import AlertDefinition, DashboardProject, SignalDefinition


@dataclass
class SignalState:
    definition: SignalDefinition
    value: Any = None
    raw_value: Any = None
    updated_at: float = 0.0
    stale: bool = True
    missing: bool = True

    def formatted_value(self) -> str:
        value = self.value if self.value is not None else self.definition.fallback_value
        if value is None:
            return "--"
        try:
            if self.definition.signal_type.value in {"float", "integer"}:
                return self.definition.format_string.format(value=value)
        except Exception:
            return str(value)
        if self.definition.enum_mapping:
            return self.definition.enum_mapping.get(str(value), str(value))
        return str(value)


class SignalStore:
    def __init__(self, signals: Iterable[SignalDefinition]):
        self._definitions = {signal.signal_id: signal for signal in signals}
        self._states = {signal_id: SignalState(definition=definition) for signal_id, definition in self._definitions.items()}

    @property
    def states(self) -> Dict[str, SignalState]:
        return self._states

    def update(self, signal_id: str, value: Any, timestamp: Optional[float] = None) -> SignalState:
        state = self._states[signal_id]
        timestamp = time.monotonic() if timestamp is None else timestamp
        state.raw_value = value
        state.updated_at = timestamp
        state.stale = False
        state.missing = False
        state.value = self._apply_signal_policy(state, value)
        return state

    def tick(self, now: Optional[float] = None) -> None:
        now = time.monotonic() if now is None else now
        for state in self._states.values():
            if state.updated_at <= 0:
                state.stale = True
                state.missing = True
                if state.definition.fallback_value is not None:
                    state.value = state.definition.fallback_value
                continue
            delta_ms = (now - state.updated_at) * 1000.0
            if delta_ms > state.definition.timeout_ms:
                state.stale = True
                if state.definition.fallback_value is not None:
                    state.value = state.definition.fallback_value

    def snapshot(self) -> Dict[str, Dict[str, Any]]:
        return {
            signal_id: {
                "value": state.value,
                "formatted": state.formatted_value(),
                "stale": state.stale,
                "missing": state.missing,
            }
            for signal_id, state in self._states.items()
        }

    def _apply_signal_policy(self, state: SignalState, new_value: Any) -> Any:
        definition = state.definition
        if state.value is not None and isinstance(new_value, (float, int)) and isinstance(state.value, (float, int)):
            if definition.deadband and abs(new_value - state.value) < definition.deadband:
                return state.value
            if definition.smoothing_factor:
                alpha = max(0.0, min(1.0, definition.smoothing_factor))
                return (state.value * alpha) + (new_value * (1.0 - alpha))
        return new_value


@dataclass
class ActiveAlert:
    alert_id: str
    severity: str
    message: str
    signal_id: str
    signal_value: Any


class AlertEngine:
    def __init__(self, alerts: Iterable[AlertDefinition]):
        self._alerts = list(alerts)
        self._last_fired: Dict[str, float] = {}

    def evaluate(self, store: SignalStore, now: Optional[float] = None) -> List[ActiveAlert]:
        now = time.monotonic() if now is None else now
        active: List[ActiveAlert] = []
        for definition in self._alerts:
            state = store.states[definition.signal_id]
            if state.missing:
                continue
            if self._compare(state.value, definition.operator, definition.threshold):
                last_fired = self._last_fired.get(definition.alert_id, 0.0)
                if definition.cooldown_ms and (now - last_fired) * 1000.0 < definition.cooldown_ms:
                    continue
                self._last_fired[definition.alert_id] = now
                active.append(
                    ActiveAlert(
                        alert_id=definition.alert_id,
                        severity=definition.severity.value,
                        message=definition.message.format(value=state.value, signal=definition.signal_id),
                        signal_id=definition.signal_id,
                        signal_value=state.value,
                    )
                )
        return active

    def _compare(self, value: Any, operator: str, threshold: Any) -> bool:
        if operator == ">":
            return value > threshold
        if operator == ">=":
            return value >= threshold
        if operator == "<":
            return value < threshold
        if operator == "<=":
            return value <= threshold
        if operator == "==":
            return value == threshold
        if operator == "!=":
            return value != threshold
        if operator == "contains":
            return str(threshold) in str(value)
        return False


class MockTelemetryBackend:
    def __init__(self) -> None:
        self._tick = itertools.count()

    def poll(self) -> Dict[str, Any]:
        tick = next(self._tick)
        rpm = 2500 + int(2500 * (1 + math.sin(tick / 2.0)))
        speed = 35 + round(20 * (1 + math.sin(tick / 4.0)), 1)
        gear = ["N", "1", "2", "3", "4", "5", "6"][tick % 7]
        battery = round(320.0 + math.sin(tick / 5.0) * 6.0, 2)
        can_health = 100 - (tick % 6) * 3
        return {
            "engine_rpm": rpm,
            "vehicle_speed": speed,
            "gear": gear,
            "battery_voltage": battery,
            "can_bus_health": can_health,
        }


@dataclass
class RuntimeContext:
    project: DashboardProject
    store: SignalStore = field(init=False)
    alert_engine: AlertEngine = field(init=False)
    backend: MockTelemetryBackend = field(default_factory=MockTelemetryBackend)
    current_page_index: int = 0

    def __post_init__(self) -> None:
        self.store = SignalStore(self.project.signals)
        self.alert_engine = AlertEngine(self.project.alerts)

    @property
    def current_page(self):
        if not self.project.pages:
            return None
        return self.project.pages[self.current_page_index % len(self.project.pages)]

    def tick(self, now: Optional[float] = None) -> List[ActiveAlert]:
        sample = self.backend.poll()
        timestamp = time.monotonic() if now is None else now
        for signal_id, value in sample.items():
            if signal_id in self.store.states:
                self.store.update(signal_id, value, timestamp=timestamp)
        self.store.tick(now=timestamp)
        return self.alert_engine.evaluate(self.store, now=timestamp)

    def next_page(self) -> None:
        if self.project.pages:
            self.current_page_index = (self.current_page_index + 1) % len(self.project.pages)

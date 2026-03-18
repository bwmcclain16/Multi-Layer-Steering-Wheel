from __future__ import annotations

from dataclasses import dataclass
from time import time
from typing import Any

from ..models import DashboardProject, SignalDefinition, SignalFallbackPolicy, SignalFreshnessPolicy, SignalQualityState


@dataclass(slots=True)
class SignalRuntimeState:
    signal_id: str
    value: Any = None
    timestamp: float | None = None
    quality: SignalQualityState = SignalQualityState.MISSING
    last_valid_value: Any = None
    fallback_active: bool = False


class SignalStore:
    def __init__(self, project: DashboardProject):
        self._definitions: dict[str, SignalDefinition] = {signal.id: signal for signal in project.signals}
        self._states: dict[str, SignalRuntimeState] = {
            signal.id: SignalRuntimeState(signal_id=signal.id) for signal in project.signals
        }

    def definitions(self) -> dict[str, SignalDefinition]:
        return dict(self._definitions)

    def update(self, signal_id: str, value: Any, *, timestamp: float | None = None) -> SignalRuntimeState:
        if signal_id not in self._states:
            raise KeyError(f"Unknown signal id: {signal_id}")
        state = self._states[signal_id]
        state.value = value
        state.timestamp = timestamp if timestamp is not None else time()
        state.quality = SignalQualityState.VALID
        state.last_valid_value = value
        state.fallback_active = False
        return state

    def get(self, signal_id: str, *, now: float | None = None) -> SignalRuntimeState:
        if signal_id not in self._states:
            raise KeyError(f"Unknown signal id: {signal_id}")
        state = self._states[signal_id]
        definition = self._definitions[signal_id]
        return self._apply_freshness(definition, state, now=now)

    def snapshot(self, *, now: float | None = None) -> dict[str, SignalRuntimeState]:
        return {signal_id: self.get(signal_id, now=now) for signal_id in self._states}

    def _apply_freshness(
        self,
        definition: SignalDefinition,
        state: SignalRuntimeState,
        *,
        now: float | None,
    ) -> SignalRuntimeState:
        if state.timestamp is None:
            return self._apply_missing_fallback(state, definition.fallback)

        freshness = definition.freshness or SignalFreshnessPolicy()
        current_time = now if now is not None else time()
        age_ms = (current_time - state.timestamp) * 1000.0

        if freshness.missing_after_ms is not None and age_ms >= freshness.missing_after_ms:
            state.quality = SignalQualityState.MISSING
            return self._apply_missing_fallback(state, definition.fallback)
        if freshness.stale_after_ms is not None and age_ms >= freshness.stale_after_ms:
            state.quality = SignalQualityState.STALE
            return state

        state.quality = SignalQualityState.VALID
        return state

    def _apply_missing_fallback(
        self,
        state: SignalRuntimeState,
        fallback: SignalFallbackPolicy | None,
    ) -> SignalRuntimeState:
        if fallback is None:
            return state
        if fallback.mode == "freeze-last" and state.last_valid_value is not None:
            state.value = state.last_valid_value
            state.quality = SignalQualityState.FROZEN
            state.fallback_active = True
        elif fallback.mode == "default-value":
            state.value = fallback.default_value
            state.quality = SignalQualityState.SUBSTITUTED
            state.fallback_active = True
        elif fallback.mode == "null":
            state.value = None
            state.quality = SignalQualityState.SUBSTITUTED
            state.fallback_active = True
        return state

from __future__ import annotations

import ast
from dataclasses import dataclass
from time import time
from typing import Any

from ..models import AlertDefinition, DashboardProject
from .signals import SignalStore


@dataclass(slots=True)
class AlertRuntimeState:
    alert_id: str
    active: bool
    severity: str
    priority: int
    acknowledged: bool = False
    last_changed_at: float | None = None


class SafeExpressionEvaluator(ast.NodeVisitor):
    def __init__(self, signal_store: SignalStore, active_states: dict[str, AlertRuntimeState] | None = None):
        self.signal_store = signal_store
        self.active_states = active_states or {}

    def evaluate(self, expression: str) -> Any:
        node = ast.parse(expression, mode="eval")
        return self.visit(node.body)

    def visit_Constant(self, node: ast.Constant) -> Any:
        return node.value

    def visit_Name(self, node: ast.Name) -> Any:
        if node.id in {"True", "False", "None"}:
            return {"True": True, "False": False, "None": None}[node.id]
        raise ValueError(f"Unsupported name: {node.id}")

    def visit_BoolOp(self, node: ast.BoolOp) -> Any:
        values = [self.visit(value) for value in node.values]
        if isinstance(node.op, ast.And):
            return all(values)
        if isinstance(node.op, ast.Or):
            return any(values)
        raise ValueError("Unsupported boolean operation")

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        operand = self.visit(node.operand)
        if isinstance(node.op, ast.Not):
            return not operand
        if isinstance(node.op, ast.USub):
            return -operand
        raise ValueError("Unsupported unary operator")

    def visit_Compare(self, node: ast.Compare) -> Any:
        left = self.visit(node.left)
        for operator, comparator in zip(node.ops, node.comparators):
            right = self.visit(comparator)
            if isinstance(operator, ast.Eq) and not (left == right):
                return False
            elif isinstance(operator, ast.NotEq) and not (left != right):
                return False
            elif isinstance(operator, ast.Lt) and not (left < right):
                return False
            elif isinstance(operator, ast.LtE) and not (left <= right):
                return False
            elif isinstance(operator, ast.Gt) and not (left > right):
                return False
            elif isinstance(operator, ast.GtE) and not (left >= right):
                return False
            left = right
        return True

    def visit_Call(self, node: ast.Call) -> Any:
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only simple function calls are supported")
        args = [self.visit(arg) for arg in node.args]
        match node.func.id:
            case "signal":
                return self.signal_store.get(args[0]).value
            case "quality":
                return str(self.signal_store.get(args[0]).quality)
            case "is_stale":
                return str(self.signal_store.get(args[0]).quality) == "stale"
            case "is_missing":
                return str(self.signal_store.get(args[0]).quality) in {"missing", "substituted", "frozen"}
            case "has_active_alert_severity":
                return any(state.active and state.severity == args[0] for state in self.active_states.values())
            case _:
                raise ValueError(f"Unsupported function: {node.func.id}")

    def generic_visit(self, node: ast.AST) -> Any:
        raise ValueError(f"Unsupported expression node: {node.__class__.__name__}")


class AlertEngine:
    def __init__(self, project: DashboardProject):
        self._alerts = sorted(project.alerts, key=lambda alert: (-alert.priority, alert.id))
        self._states: dict[str, AlertRuntimeState] = {
            alert.id: AlertRuntimeState(
                alert_id=alert.id,
                active=False,
                severity=str(alert.severity),
                priority=alert.priority,
                last_changed_at=None,
            )
            for alert in self._alerts
        }

    def evaluate(self, signal_store: SignalStore) -> list[AlertRuntimeState]:
        evaluator = SafeExpressionEvaluator(signal_store=signal_store, active_states=self._states)
        current_time = time()
        for alert in self._alerts:
            state = self._states[alert.id]
            result = bool(evaluator.evaluate(alert.condition)) if alert.enabled else False
            if result != state.active:
                state.active = result
                state.last_changed_at = current_time
                if not result:
                    state.acknowledged = False
        return sorted(self._states.values(), key=lambda item: (-item.priority, item.alert_id))

    def acknowledge(self, alert_id: str) -> None:
        if alert_id in self._states:
            self._states[alert_id].acknowledged = True

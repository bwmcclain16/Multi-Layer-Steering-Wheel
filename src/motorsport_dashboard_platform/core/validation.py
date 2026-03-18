from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence

from .models import DashboardProject


@dataclass
class ValidationIssue:
    level: str
    path: str
    message: str


OPERATORS = {">", ">=", "<", "<=", "==", "!=", "contains"}


def validate_project(project: DashboardProject) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    signal_ids = _duplicate_ids([signal.signal_id for signal in project.signals], "signals")
    issues.extend(signal_ids)
    page_ids = {page.page_id for page in project.pages}
    theme_ids = {theme.theme_id for theme in project.themes}
    backend_ids = {backend.backend_id for backend in project.backends}
    alert_ids = {alert.alert_id for alert in project.alerts}
    peripheral_ids = {peripheral.peripheral_id for peripheral in project.peripherals}
    can_signal_ids = {item.signal_id for item in project.can_signals}

    for signal in project.signals:
        if signal.timeout_ms <= 0:
            issues.append(ValidationIssue("error", f"signals.{signal.signal_id}.timeout_ms", "Timeout must be positive."))
        if not signal.display_name:
            issues.append(ValidationIssue("error", f"signals.{signal.signal_id}.display_name", "Display name is required."))

    for page in project.pages:
        if page.theme_id not in theme_ids:
            issues.append(ValidationIssue("error", f"pages.{page.page_id}.theme_id", "Unknown theme reference."))
        for widget in page.widgets:
            if widget.signal_id not in {signal.signal_id for signal in project.signals}:
                issues.append(ValidationIssue("error", f"pages.{page.page_id}.widgets.{widget.widget_id}.signal_id", "Unknown signal reference."))

    for alert in project.alerts:
        if alert.signal_id not in {signal.signal_id for signal in project.signals}:
            issues.append(ValidationIssue("error", f"alerts.{alert.alert_id}.signal_id", "Unknown signal reference."))
        if alert.operator not in OPERATORS:
            issues.append(ValidationIssue("error", f"alerts.{alert.alert_id}.operator", "Unsupported operator."))

    for profile in project.profiles:
        if profile.default_page_id and profile.default_page_id not in page_ids:
            issues.append(ValidationIssue("error", f"profiles.{profile.profile_id}.default_page_id", "Unknown default page."))
        for page_id in profile.page_ids:
            if page_id not in page_ids:
                issues.append(ValidationIssue("error", f"profiles.{profile.profile_id}.page_ids", f"Unknown page '{page_id}'."))
        for backend_id in profile.enabled_backend_ids:
            if backend_id not in backend_ids:
                issues.append(ValidationIssue("error", f"profiles.{profile.profile_id}.enabled_backend_ids", f"Unknown backend '{backend_id}'."))

    for mapping in project.can_mappings:
        if mapping.can_signal_id not in can_signal_ids:
            issues.append(ValidationIssue("error", f"can_mappings.{mapping.can_signal_id}", "Unknown CAN signal reference."))
        if mapping.normalized_signal_id not in {signal.signal_id for signal in project.signals}:
            issues.append(ValidationIssue("error", f"can_mappings.{mapping.can_signal_id}", "Unknown normalized signal reference."))

    for rule in project.hardware_rules:
        if rule.peripheral_id not in peripheral_ids:
            issues.append(ValidationIssue("error", f"hardware_rules.{rule.rule_id}.peripheral_id", "Unknown peripheral reference."))
        if rule.trigger_alert_id and rule.trigger_alert_id not in alert_ids:
            issues.append(ValidationIssue("error", f"hardware_rules.{rule.rule_id}.trigger_alert_id", "Unknown alert reference."))

    return issues


def _duplicate_ids(values: Sequence[str], root: str) -> Iterable[ValidationIssue]:
    seen = set()
    duplicates = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return [ValidationIssue("error", f"{root}.{value}", "Duplicate identifier.") for value in sorted(duplicates)]

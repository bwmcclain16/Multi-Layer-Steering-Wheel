from __future__ import annotations

from dataclasses import dataclass, field

from .models import DashboardProject, PageDefinition, ProfileDefinition, SignalDefinition


@dataclass(slots=True)
class ValidationIssue:
    message: str
    path: str
    level: str = "error"


@dataclass(slots=True)
class ValidationReport:
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not any(issue.level == "error" for issue in self.issues)

    def add(self, message: str, path: str, *, level: str = "error") -> None:
        self.issues.append(ValidationIssue(message=message, path=path, level=level))


class ProjectValidator:
    def validate(self, project: DashboardProject) -> ValidationReport:
        report = ValidationReport()
        self._validate_unique_ids(project, report)
        self._validate_signal_ranges(project.signals, report)
        self._validate_references(project, report)
        self._validate_profiles(project.profiles, project, report)
        return report

    def _validate_unique_ids(self, project: DashboardProject, report: ValidationReport) -> None:
        collections = {
            "assets": project.assets,
            "signals": project.signals,
            "backends": project.backends,
            "can_buses": project.can_buses,
            "can_messages": project.can_messages,
            "can_signals": project.can_signals,
            "mappings": project.mappings,
            "themes": project.themes,
            "widgets": project.widgets,
            "pages": project.pages,
            "alerts": project.alerts,
            "peripherals": project.peripherals,
            "hardware_rules": project.hardware_rules,
            "profiles": project.profiles,
        }
        for name, items in collections.items():
            seen: set[str] = set()
            for item in items:
                item_id = getattr(item, "id")
                if item_id in seen:
                    report.add(f"Duplicate id '{item_id}' found in {name}.", f"{name}.{item_id}")
                seen.add(item_id)

    def _validate_signal_ranges(self, signals: list[SignalDefinition], report: ValidationReport) -> None:
        for signal in signals:
            if signal.expected_range and signal.expected_range.min is not None and signal.expected_range.max is not None:
                if signal.expected_range.min > signal.expected_range.max:
                    report.add(
                        f"Signal '{signal.id}' has min greater than max.",
                        f"signals.{signal.id}.expected_range",
                    )

    def _validate_references(self, project: DashboardProject, report: ValidationReport) -> None:
        signal_ids = {item.id for item in project.signals}
        backend_ids = {item.id for item in project.backends}
        page_ids = {item.id for item in project.pages}
        theme_ids = {item.id for item in project.themes}
        widget_ids = {item.id for item in project.widgets}
        alert_ids = {item.id for item in project.alerts}
        peripheral_ids = {item.id for item in project.peripherals}
        hardware_rule_ids = {item.id for item in project.hardware_rules}
        can_bus_ids = {item.id for item in project.can_buses}
        can_message_ids = {item.id for item in project.can_messages}
        can_signal_ids = {item.id for item in project.can_signals}

        for message in project.can_messages:
            if message.bus_id not in can_bus_ids:
                report.add(f"CAN message '{message.id}' references unknown bus '{message.bus_id}'.", f"can_messages.{message.id}.bus_id")

        for signal in project.can_signals:
            if signal.message_id not in can_message_ids:
                report.add(f"CAN signal '{signal.id}' references unknown message '{signal.message_id}'.", f"can_signals.{signal.id}.message_id")

        for mapping in project.mappings:
            if mapping.signal_id not in signal_ids:
                report.add(f"Mapping '{mapping.id}' references unknown signal '{mapping.signal_id}'.", f"mappings.{mapping.id}.signal_id")
            if mapping.backend_id not in backend_ids:
                report.add(f"Mapping '{mapping.id}' references unknown backend '{mapping.backend_id}'.", f"mappings.{mapping.id}.backend_id")
            if mapping.source_type == "can-decode" and mapping.source_ref not in can_signal_ids:
                report.add(f"Mapping '{mapping.id}' references unknown CAN decode '{mapping.source_ref}'.", f"mappings.{mapping.id}.source_ref")

        for page in project.pages:
            self._validate_page(page, widget_ids, theme_ids, report)

        for widget in project.widgets:
            for binding in widget.bindings:
                if binding.signal_id not in signal_ids:
                    report.add(f"Widget '{widget.id}' references unknown signal '{binding.signal_id}'.", f"widgets.{widget.id}.bindings.{binding.key}")

        for rule in project.hardware_rules:
            if rule.peripheral_id not in peripheral_ids:
                report.add(f"Hardware rule '{rule.id}' references unknown peripheral '{rule.peripheral_id}'.", f"hardware_rules.{rule.id}.peripheral_id")

        self._reference_sets = {
            "pages": page_ids,
            "themes": theme_ids,
            "alerts": alert_ids,
            "peripherals": peripheral_ids,
            "hardware_rules": hardware_rule_ids,
            "backends": backend_ids,
            "mappings": {item.id for item in project.mappings},
        }

    def _validate_page(self, page: PageDefinition, widget_ids: set[str], theme_ids: set[str], report: ValidationReport) -> None:
        for widget_id in page.widget_ids:
            if widget_id not in widget_ids:
                report.add(f"Page '{page.id}' references unknown widget '{widget_id}'.", f"pages.{page.id}.widget_ids")
        if page.theme_override_id and page.theme_override_id not in theme_ids:
            report.add(f"Page '{page.id}' references unknown theme '{page.theme_override_id}'.", f"pages.{page.id}.theme_override_id")

    def _validate_profiles(self, profiles: list[ProfileDefinition], project: DashboardProject, report: ValidationReport) -> None:
        ref = self._reference_sets
        for profile in profiles:
            if profile.default_page_id not in ref["pages"]:
                report.add(f"Profile '{profile.id}' references unknown default page '{profile.default_page_id}'.", f"profiles.{profile.id}.default_page_id")
            if profile.theme_id not in ref["themes"]:
                report.add(f"Profile '{profile.id}' references unknown theme '{profile.theme_id}'.", f"profiles.{profile.id}.theme_id")
            for collection_name, values in {
                "backend_ids": profile.backend_ids,
                "mapping_ids": profile.mapping_ids,
                "page_ids": profile.page_ids,
                "alert_ids": profile.alert_ids,
                "peripheral_ids": profile.peripheral_ids,
                "hardware_rule_ids": profile.hardware_rule_ids,
            }.items():
                target_set = ref[collection_name.removesuffix("_ids") + "s"] if collection_name in {"backend_ids", "mapping_ids", "page_ids", "alert_ids", "peripheral_ids"} else ref["hardware_rules"]
                for value in values:
                    if value not in target_set:
                        report.add(f"Profile '{profile.id}' references unknown id '{value}' in {collection_name}.", f"profiles.{profile.id}.{collection_name}")
            if profile.default_page_id not in profile.page_ids:
                report.add(f"Profile '{profile.id}' default page must be included in page_ids.", f"profiles.{profile.id}.default_page_id")

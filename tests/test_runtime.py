import unittest

from motorsport_dashboard_platform.example_project import create_example_project
from motorsport_dashboard_platform.runtime.rules import AlertEngine
from motorsport_dashboard_platform.runtime.signals import SignalStore


class RuntimeTests(unittest.TestCase):
    def test_signal_store_marks_stale_and_missing(self) -> None:
        project = create_example_project()
        store = SignalStore(project)
        store.update("vehicle.speed", 123, timestamp=100.0)

        stale_state = store.get("vehicle.speed", now=100.3)
        self.assertEqual(str(stale_state.quality), "stale")

        missing_state = store.get("vehicle.speed", now=101.3)
        self.assertIn(str(missing_state.quality), {"frozen", "substituted", "missing"})

    def test_alert_engine_evaluates_conditions(self) -> None:
        project = create_example_project()
        store = SignalStore(project)
        store.update("system.can.bus0.health", "timeout")
        store.update("vehicle.battery.voltage", 250)

        states = AlertEngine(project).evaluate(store)
        active_alert_ids = {state.alert_id for state in states if state.active}
        self.assertIn("alert-can-timeout", active_alert_ids)
        self.assertIn("alert-low-battery", active_alert_ids)


if __name__ == "__main__":
    unittest.main()

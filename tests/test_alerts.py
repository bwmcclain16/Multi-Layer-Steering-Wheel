import unittest

from motorsport_dashboard_platform.core.example_project import build_example_project
from motorsport_dashboard_platform.core.runtime import AlertEngine, SignalStore


class AlertTests(unittest.TestCase):
    def test_alert_fires_when_threshold_crossed(self):
        project = build_example_project()
        store = SignalStore(project.signals)
        alert_engine = AlertEngine(project.alerts)
        store.update("engine_rpm", 8000, timestamp=1.0)
        store.tick(now=1.0)
        active = alert_engine.evaluate(store, now=1.0)
        self.assertTrue(any(alert.alert_id == "rpm-high" for alert in active))


if __name__ == "__main__":
    unittest.main()

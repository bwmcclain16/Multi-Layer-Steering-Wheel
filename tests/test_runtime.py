import unittest

from motorsport_dashboard_platform.core.example_project import build_example_project
from motorsport_dashboard_platform.core.runtime import SignalStore


class RuntimeTests(unittest.TestCase):
    def test_signal_store_deadband_and_timeout(self):
        signal = build_example_project().signals[1]
        signal.deadband = 1.0
        signal.timeout_ms = 100
        signal.fallback_value = 0.0
        store = SignalStore([signal])
        store.update(signal.signal_id, 50.0, timestamp=1.0)
        store.update(signal.signal_id, 50.5, timestamp=1.01)
        self.assertEqual(50.0, store.states[signal.signal_id].value)
        store.tick(now=1.2)
        self.assertTrue(store.states[signal.signal_id].stale)
        self.assertEqual(0.0, store.states[signal.signal_id].value)


if __name__ == "__main__":
    unittest.main()

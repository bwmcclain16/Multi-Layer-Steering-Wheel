import unittest

from motorsport_dashboard_platform.dash.controller import DashController


class DashControllerTests(unittest.TestCase):
    def test_headless_run_produces_snapshots(self):
        controller = DashController()
        snapshots = controller.headless_run(ticks=2)
        self.assertEqual(2, len(snapshots))
        self.assertTrue(snapshots[0].widgets)
        self.assertEqual("Race Main", snapshots[0].page_name)


if __name__ == "__main__":
    unittest.main()

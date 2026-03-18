import unittest

from motorsport_dashboard_platform.core.models import SignalDefinition, SignalType
from motorsport_dashboard_platform.editor.controller import EditorController


class EditorControllerTests(unittest.TestCase):
    def test_upsert_signal_and_metadata(self):
        controller = EditorController()
        controller.update_metadata(name="Updated Project")
        controller.upsert_signal(
            SignalDefinition(
                signal_id="oil_temp",
                display_name="Oil Temp",
                category="engine",
                signal_type=SignalType.FLOAT,
                units="C",
            )
        )
        self.assertEqual("Updated Project", controller.project.metadata.name)
        self.assertTrue(any(signal.signal_id == "oil_temp" for signal in controller.project.signals))


if __name__ == "__main__":
    unittest.main()

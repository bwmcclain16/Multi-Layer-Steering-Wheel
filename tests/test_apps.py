import unittest

from motorsport_dashboard_platform.apps.dash_app import DashController
from motorsport_dashboard_platform.apps.editor_app import EditorController
from motorsport_dashboard_platform.example_project import create_example_project


class ApplicationTests(unittest.TestCase):
    def test_editor_controller_validation(self) -> None:
        controller = EditorController(create_example_project())
        lines = controller.validate()
        self.assertIn("Project is valid.", lines)

    def test_editor_controller_can_create_and_update_entities(self) -> None:
        controller = EditorController(create_example_project())
        signal = controller.create_signal()
        controller.upsert_signal(
            signal_id=signal.id,
            display_name="Updated Signal",
            category="custom",
            data_type="number",
            units="V",
            stale_after_ms=100,
            missing_after_ms=500,
            fallback_mode="default-value",
            fallback_value="0",
        )
        page = controller.create_page()
        widget = controller.create_widget(page_id=page.id)
        controller.upsert_widget(
            widget_id=widget.id,
            name="Updated Widget",
            widget_type="numeric-readout",
            x=10,
            y=20,
            width=100,
            height=50,
            anchor="top-left",
            binding_signal_id=signal.id,
            page_id=page.id,
        )
        alert = controller.create_alert()
        controller.upsert_alert(
            alert_id=alert.id,
            name="Updated Alert",
            severity="warning",
            priority=60,
            condition=f"signal('{signal.id}') > 1",
        )
        profile = controller.create_profile()
        controller.upsert_profile(
            profile_id=profile.id,
            name="Updated Profile",
            default_page_id=page.id,
            theme_id=controller.project.themes[0].id,
            page_ids_csv=page.id,
            alert_ids_csv=alert.id,
            backend_ids_csv=controller.project.backends[0].id,
            tags_csv="custom, edited",
        )
        self.assertIn(signal.id, {item.id for item in controller.project.signals})
        self.assertIn(widget.id, {item.id for item in controller.project.widgets})
        self.assertIn(alert.id, {item.id for item in controller.project.alerts})
        self.assertIn(profile.id, {item.id for item in controller.project.profiles})

    def test_dash_controller_tick_returns_snapshot(self) -> None:
        controller = DashController(create_example_project(), profile_id="profile-fsae")
        snapshot = controller.tick()
        self.assertEqual(snapshot.profile_id, "profile-fsae")
        self.assertTrue(snapshot.page_name)
        self.assertIsNotNone(snapshot.rpm)


if __name__ == "__main__":
    unittest.main()

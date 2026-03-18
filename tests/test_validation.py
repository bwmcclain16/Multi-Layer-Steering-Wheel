import unittest

from motorsport_dashboard_platform.core.example_project import build_example_project
from motorsport_dashboard_platform.core.validation import validate_project


class ValidationTests(unittest.TestCase):
    def test_example_project_is_valid(self):
        issues = validate_project(build_example_project())
        self.assertEqual([], issues)

    def test_invalid_widget_reference_is_reported(self):
        project = build_example_project()
        project.pages[0].widgets[0].signal_id = "missing"
        issues = validate_project(project)
        self.assertTrue(any("Unknown signal reference" in issue.message for issue in issues))


if __name__ == "__main__":
    unittest.main()

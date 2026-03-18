import unittest

from motorsport_dashboard_platform.example_project import create_example_project
from motorsport_dashboard_platform.validation import ProjectValidator


class ValidationTests(unittest.TestCase):
    def test_example_project_is_valid(self) -> None:
        report = ProjectValidator().validate(create_example_project())
        self.assertTrue(report.is_valid, report.issues)


if __name__ == "__main__":
    unittest.main()

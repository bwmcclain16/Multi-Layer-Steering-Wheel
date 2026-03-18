import unittest

from motorsport_dashboard_platform.example_project import create_example_project
from motorsport_dashboard_platform.project_io import project_from_dict


class ProjectIOTests(unittest.TestCase):
    def test_project_round_trip_from_dict(self) -> None:
        project = create_example_project()
        rebuilt = project_from_dict(project.to_dict())
        self.assertEqual(rebuilt.metadata.id, project.metadata.id)
        self.assertEqual(len(rebuilt.signals), len(project.signals))
        self.assertEqual(rebuilt.profiles[1].id, "profile-fsae")


if __name__ == "__main__":
    unittest.main()

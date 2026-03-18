import tempfile
import unittest
from pathlib import Path

from motorsport_dashboard_platform.core.example_project import build_example_project
from motorsport_dashboard_platform.core.project_io import load_project, save_project


class ProjectIoTests(unittest.TestCase):
    def test_round_trip(self):
        project = build_example_project()
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "project.json"
            save_project(project, path)
            loaded = load_project(path)
        self.assertEqual(project.to_dict(), loaded.to_dict())


if __name__ == "__main__":
    unittest.main()

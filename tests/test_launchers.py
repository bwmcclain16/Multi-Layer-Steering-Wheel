import subprocess
import unittest
from pathlib import Path


class LauncherTests(unittest.TestCase):
    def test_editor_launcher_runs_headless(self) -> None:
        result = subprocess.run([
            str(Path('bin/mlsw-editor')),
            '--headless',
            '--validate',
        ], check=True, capture_output=True, text=True)
        self.assertIn('Project is valid.', result.stdout)

    def test_dash_launcher_runs_headless(self) -> None:
        result = subprocess.run([
            str(Path('bin/mlsw-dash')),
            '--headless',
            '--ticks',
            '1',
        ], check=True, capture_output=True, text=True)
        self.assertIn('profile=', result.stdout)


if __name__ == '__main__':
    unittest.main()

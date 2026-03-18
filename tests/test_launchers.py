import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = os.environ.copy()
ENV["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + ENV.get("PYTHONPATH", "")


class LauncherSmokeTests(unittest.TestCase):
    def run_cmd(self, *args):
        return subprocess.run(args, cwd=ROOT, env=ENV, capture_output=True, text=True, check=True)

    def test_editor_headless_launcher(self):
        result = self.run_cmd("./bin/mlsw-editor", "--headless", "--validate")
        self.assertIn("No validation issues detected.", result.stdout)

    def test_dash_headless_launcher(self):
        result = self.run_cmd("./bin/mlsw-dash", "--headless", "--ticks", "1")
        self.assertIn("Race Main", result.stdout)


if __name__ == "__main__":
    unittest.main()

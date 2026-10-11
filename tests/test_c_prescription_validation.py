"""Validate dated C prescriptions through the real repository validator."""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.fitness.paths import ROOT


class CPrescriptionValidationTests(unittest.TestCase):
    def validate_mode(self, mode):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "data", root / "data")
            (root / "scripts").mkdir()
            shutil.copy(ROOT / "scripts/validate_fitness_data.rb", root / "scripts")
            shutil.copy(ROOT / "README.md", root)
            path = root / "data/logs/structured/sessions.yaml"
            text = path.read_text(encoding="utf-8")
            marker = "    c_mode: endurance\n"
            self.assertIn(marker, text)
            replacement = "" if mode is None else f"    c_mode: {mode}\n"
            path.write_text(text.replace(marker, replacement, 1), encoding="utf-8")
            return subprocess.run(
                ["ruby", str(root / "scripts/validate_fitness_data.rb")],
                capture_output=True, text=True,
            )

    def test_endurance_prescription_is_accepted(self):
        result = self.validate_mode("endurance")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_or_invalid_mode_is_rejected(self):
        for mode in (None, "unknown"):
            with self.subTest(mode=mode):
                result = self.validate_mode(mode)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("unknown or missing C mode", result.stderr)


if __name__ == "__main__":
    unittest.main()

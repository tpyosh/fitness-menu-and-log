"""Check that each active trial appears beside its own menu exercise."""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.fitness.paths import ROOT


class MenuTrialDisplayTests(unittest.TestCase):
    def setUp(self):
        trials = json.loads((ROOT / "data/menus/active-trials.json").read_text())
        active_a = [trial for trial in trials["trials"] if trial["menu"] == "A" and trial["status"] == "active"]
        self.assertEqual(len(active_a), 1)
        self.active_a_trial_id = active_a[0]["id"]

    def validate_with_change(self, filename, before, after):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "data", root / "data")
            (root / "scripts").mkdir()
            shutil.copy(ROOT / "scripts/validate_fitness_data.rb", root / "scripts")
            shutil.copy(ROOT / "README.md", root)
            path = root / filename
            text = path.read_text(encoding="utf-8")
            self.assertIn(before, text)
            path.write_text(text.replace(before, after, 1), encoding="utf-8")
            return subprocess.run(
                ["ruby", str(root / "scripts/validate_fitness_data.rb")],
                capture_output=True, text=True,
            )

    def test_b_lat_trial_cannot_satisfy_missing_a_quick_reference(self):
        result = self.validate_with_change(
            "README.md", "**次回Aのみ: 47kg**", "**次回Aのみ: 54kg**",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(f"trial missing from Quick Reference: {self.active_a_trial_id}", result.stderr)

    def test_b_lat_trial_cannot_satisfy_missing_a_full_menu(self):
        result = self.validate_with_change(
            "data/menus/current-menus.md", "40kg → **47kg**", "40kg → **54kg**",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(f"trial missing from current menu: {self.active_a_trial_id}", result.stderr)
        self.assertNotIn("baseline hash mismatch", result.stderr)


if __name__ == "__main__":
    unittest.main()

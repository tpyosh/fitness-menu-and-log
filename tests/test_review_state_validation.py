"""Exercise the review invariants through the repository's real validator."""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.fitness.paths import ROOT


class ReviewStateValidationTests(unittest.TestCase):
    def validate_with_change(self, filename, change):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "data", root / "data")
            (root / "scripts").mkdir()
            shutil.copy(ROOT / "scripts/validate_fitness_data.rb", root / "scripts")
            shutil.copy(ROOT / "README.md", root)
            path = root / "data/logs/reviews" / filename
            path.write_text(change(path.read_text()))
            return subprocess.run(
                ["ruby", str(root / "scripts/validate_fitness_data.rb")],
                capture_output=True, text=True,
            )

    def test_valid_current_state_is_accepted(self):
        result = self.validate_with_change("backlog.md", lambda text: text)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_unknown_judgment_reference_is_rejected(self):
        result = self.validate_with_change(
            "backlog.md", lambda text: text.replace("- decisions: J-003", "- decisions: J-999", 1),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown or missing judgment reference", result.stderr)

    def test_duplicate_judgment_id_is_rejected(self):
        result = self.validate_with_change(
            "current-assessment.md", lambda text: text.replace("## J-004：", "## J-003：", 1),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate review id", result.stderr)

    def test_resolving_without_outcome_is_rejected(self):
        result = self.validate_with_change(
            "backlog.md", lambda text: text.replace("- status: waiting", "- status: resolved", 1),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("resolved backlog lacks outcome", result.stderr)


if __name__ == "__main__":
    unittest.main()

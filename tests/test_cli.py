"""Exercise real entry points without writing records or opening Apple Notes."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.fitness.paths import ROOT


class CommandLineTests(unittest.TestCase):
    def run_cli(self, script, args, *, module=False, cwd=ROOT):
        command = (
            [sys.executable, "-m", f"scripts.{script}"]
            if module
            else [sys.executable, str(ROOT / "scripts" / f"{script}.py")]
        )
        return subprocess.run(
            [*command, *args], cwd=cwd, capture_output=True, text=True, check=True,
        )

    def test_direct_and_module_execution_match(self):
        commands = [
            ("workout_feedback", ["--date", "2026-10-04", "--menu", "A", "--completed"]),
            ("export_today_menu_to_apple_notes", [
                "--menu", "C", "--c-mode", "standard", "--date", "2026-10-10", "--dry-run",
            ]),
            ("generate_garmin_coach_review_prompt", [
                "--requested-at", "2026-10-10T12:00:00+09:00", "--dry-run",
            ]),
        ]
        for script, args in commands:
            with self.subTest(script=script):
                direct = self.run_cli(script, args)
                module = self.run_cli(script, args, module=True)
                self.assertEqual(direct.stdout, module.stdout)
                self.assertEqual(direct.stderr, module.stderr)

    def test_direct_execution_resolves_sources_outside_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            cwd = Path(directory)
            resolved = self.run_cli("workout_feedback", [
                "--date", "2026-10-04", "--menu", "C", "--c-mode", "standard", "--completed",
            ], cwd=cwd)
            self.assertEqual(json.loads(resolved.stdout)["menu"], "C")
            preview = self.run_cli("export_today_menu_to_apple_notes", [
                "--menu", "C", "--c-mode", "standard", "--dry-run",
            ], cwd=cwd)
            self.assertIn("## Standard（45分）", preview.stdout)
            review = self.run_cli("generate_garmin_coach_review_prompt", [
                "--requested-at", "2026-10-10T12:00:00+09:00", "--dry-run",
            ], cwd=cwd)
            self.assertIn("# ChatGPT Garmin Coaching Review Request", review.stdout)
            self.assertEqual(list(cwd.iterdir()), [])

    def test_review_dry_run_does_not_write_prompt_or_review_state(self):
        paths = [ROOT / "data/logs/reviews" / name for name in (
            "review-request-state.json", "current-assessment.md", "backlog.md",
        )]
        before = {path: path.read_bytes() for path in paths}
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "review.md"
            self.run_cli("generate_garmin_coach_review_prompt", [
                "--requested-at", "2026-10-10T12:00:00+09:00",
                "--output", str(output), "--dry-run",
            ])
            self.assertFalse(output.exists())
        self.assertEqual({path: path.read_bytes() for path in paths}, before)


if __name__ == "__main__":
    unittest.main()

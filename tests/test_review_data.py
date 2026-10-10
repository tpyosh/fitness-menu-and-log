import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.fitness import review_data


class ReviewDataTests(unittest.TestCase):
    def test_history_reports_malformed_line_with_location(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.jsonl"
            path.write_text('{"requested_at":"2026-10-04"}\n\ninvalid\n', encoding="utf-8")
            with patch.object(review_data, "HISTORY_PATH", path):
                with self.assertRaisesRegex(SystemExit, "history.jsonl:3"):
                    review_data.load_history()

    def test_missing_history_and_yaml_are_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing"
            with patch.object(review_data, "HISTORY_PATH", path):
                self.assertEqual(review_data.load_history(), [])
            with patch.object(review_data, "SESSIONS_YAML", path):
                self.assertEqual(review_data.load_yaml_details(), {})
                self.assertEqual(review_data.load_yaml_excerpt_details(), {})

    def test_csv_sessions_are_sorted_by_date(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sessions.csv"
            path.write_text(
                "date,session_type\n2026-10-04,A_full\n2026-09-11,B_full\n", encoding="utf-8",
            )
            with patch.object(review_data, "SESSIONS_CSV", path):
                sessions = review_data.load_sessions()
            self.assertEqual([row["date"] for row in sessions], ["2026-09-11", "2026-10-04"])

    def test_yaml_fallback_keeps_session_boundaries_and_provenance(self):
        first = (
            '  - date: "2026-09-11"\n'
            "    session_type: B_full\n"
            "    effective_execution:\n"
            "      provenance: prescribed_no_deviation_reported\n"
        )
        second = (
            '  - date: "2026-10-04"\n'
            "    session_type: A_full\n"
            "    reported_deviations: []\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sessions.yaml"
            path.write_text("sessions:\n" + first + second, encoding="utf-8")
            with patch.object(review_data, "SESSIONS_YAML", path):
                details = review_data.load_yaml_excerpt_details()
            self.assertEqual(set(details), {("2026-09-11", "B_full"), ("2026-10-04", "A_full")})
            self.assertEqual(details[("2026-09-11", "B_full")]["raw_yaml_excerpt"], first.rstrip("\n"))
            self.assertEqual(details[("2026-10-04", "A_full")]["raw_yaml_excerpt"], second.rstrip("\n"))


if __name__ == "__main__":
    unittest.main()

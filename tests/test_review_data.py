import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.fitness import review_data


class ReviewDataTests(unittest.TestCase):
    def test_request_state_reports_malformed_json_with_location(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            path.write_text('{\ninvalid\n', encoding="utf-8")
            with patch.object(review_data, "REQUEST_STATE", path):
                with self.assertRaisesRegex(SystemExit, "state.json:2"):
                    review_data.load_request_state()

    def test_missing_request_state_and_yaml_are_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing"
            with patch.object(review_data, "REQUEST_STATE", path):
                self.assertIsNone(review_data.load_request_state())
            with patch.object(review_data, "SESSIONS_YAML", path):
                self.assertEqual(review_data.load_yaml_details(), {})
                self.assertEqual(review_data.load_yaml_excerpt_details(), {})

    def test_request_uses_fixed_output_and_protects_review_sources(self):
        first = review_data.parse_requested_at("2026-10-10T12:00:00+09:00")
        second = review_data.parse_requested_at("2026-10-11T12:00:00+09:00")
        self.assertEqual(review_data.choose_output_path(first, None), review_data.choose_output_path(second, None))
        for path in (review_data.REVIEW_ASSESSMENT, review_data.REVIEW_BACKLOG, review_data.REQUEST_STATE):
            with self.subTest(path=path), self.assertRaisesRegex(SystemExit, "Cannot overwrite review source"):
                review_data.choose_output_path(first, path)

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

import unittest
from datetime import datetime

from scripts import generate_garmin_coach_review_prompt as MODULE
from scripts.fitness.review_rendering import render_prompt


class ReviewPromptExecutionTests(unittest.TestCase):
    def test_renderer_uses_supplied_sources_without_repository_files(self):
        output = render_prompt(
            datetime.fromisoformat("2026-10-10T12:00:00+09:00"),
            None, [], [], {}, "review focus",
            design_philosophy="supplied philosophy",
            current_menus="supplied menus",
            sources=["source.md"],
        )
        self.assertIn("supplied philosophy", output)
        self.assertIn("supplied menus", output)
        self.assertIn("  - source.md", output)
        self.assertIn("review focus", output)
        self.assertIn("前回レビュー依頼以降の新規Garminログはありません", output)

    def test_review_handoff_preserves_execution_provenance(self):
        row = {
            "date": "2026-10-04", "session_type": "A_full", "duration_min": "62.88",
            "avg_hr": "121", "max_hr": "160", "aerobic_te": "3.0",
            "anaerobic_te": "0.5", "exercise_load": "76", "calories": "383",
            "primary_benefit": "Base", "zone1_time": "25:35", "zone2_time": "11:17",
            "zone3_time": "12:19", "zone4_time": "12:26", "zone5_time": "0:00",
            "subjective_fatigue": "mixed", "soreness_next_day": "none",
            "menu_deviation": "none", "notes": "test",
        }
        detail = {
            ("2026-10-04", "A_full"): {
                "prescription_id": "2026-08-31-baseline",
                "effective_execution": {
                    "machine_weights": {
                        "lat_pulldown": {
                            "weight_kg": 40,
                            "provenance": "prescribed_no_deviation_reported",
                        }
                    }
                },
            }
        }
        output = MODULE.format_session(row, detail)
        self.assertIn("2026-08-31-baseline", output)
        self.assertIn("prescribed_no_deviation_reported", output)


if __name__ == "__main__":
    unittest.main()

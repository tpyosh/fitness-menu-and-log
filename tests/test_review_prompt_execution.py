import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/generate_garmin_coach_review_prompt.py"
SPEC = importlib.util.spec_from_file_location("garmin_review_prompt", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReviewPromptExecutionTests(unittest.TestCase):
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

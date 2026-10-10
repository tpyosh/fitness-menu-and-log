import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from scripts import workout_feedback as MODULE

ROOT = Path(__file__).resolve().parents[1]


class WorkoutFeedbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = MODULE.load_json(MODULE.PRESCRIPTIONS)
        cls.trials = MODULE.load_json(MODULE.TRIALS)
        MODULE.validate_manifest(cls.manifest)
        MODULE.validate_trials(cls.trials, cls.manifest)
        _, cls.a_menu = MODULE.resolve_prescription(cls.manifest, "2026-10-04", "A")

    def test_prescribed_values_are_effective_without_reasking(self):
        effective = MODULE.interpret_execution(self.a_menu, completed_as_prescribed=True)
        lat = next(item for item in effective if item["id"] == "lat_pulldown")
        self.assertEqual((lat["weight_kg"], lat["reps_min"], lat["reps_max"], lat["sets"]), (40, 8, 12, 2))
        self.assertEqual(lat["provenance"]["weight_kg"], "prescribed_no_deviation_reported")
        self.assertNotIn("actual_reps", lat)

    def test_explicit_deviation_changes_only_target(self):
        effective = MODULE.interpret_execution(
            self.a_menu, completed_as_prescribed=True,
            reported_deviations=[{"exercise_id": "lat_pulldown", "fields": {"weight_kg": 47}}],
        )
        values = {item["id"]: item for item in effective}
        self.assertEqual(values["lat_pulldown"]["weight_kg"], 47)
        self.assertEqual(values["lat_pulldown"]["provenance"]["weight_kg"], "user_reported")
        self.assertEqual(values["chest_press"]["weight_kg"], 33)

    def test_missing_garmin_weight_does_not_erase_prescription(self):
        effective = MODULE.interpret_execution(self.a_menu, completed_as_prescribed=True, observations=[])
        self.assertEqual(next(item for item in effective if item["id"] == "seated_leg_press")["weight_kg"], 125)

    def test_garmin_observation_can_override_baseline(self):
        effective = MODULE.interpret_execution(
            self.a_menu, completed_as_prescribed=True,
            observations=[{"exercise_id": "treadmill_main", "fields": {"actual_duration_min": 18.08}}],
        )
        main = next(item for item in effective if item["id"] == "treadmill_main")
        self.assertEqual(main["actual_duration_min"], 18.08)
        self.assertEqual(main["provenance"]["actual_duration_min"], "observed")
        self.assertEqual(sum(step["duration_min"] for step in main["steps"]), 18)

    def test_two_direct_sources_conflicting_require_resolution(self):
        with self.assertRaises(MODULE.ObservationConflict):
            MODULE.interpret_execution(
                self.a_menu, completed_as_prescribed=True,
                reported_deviations=[{"exercise_id": "lat_pulldown", "fields": {"weight_kg": 47}}],
                observations=[{"exercise_id": "lat_pulldown", "fields": {"weight_kg": 40}}],
            )

    def test_partial_user_input_preserves_all_other_fields(self):
        effective = MODULE.interpret_execution(
            self.a_menu, completed_as_prescribed=True,
            reported_deviations=[{"exercise_id": "chest_press", "fields": {"actual_reps": 10}}],
        )
        chest = next(item for item in effective if item["id"] == "chest_press")
        self.assertEqual(chest["actual_reps"], 10)
        self.assertEqual(chest["weight_kg"], 33)
        self.assertEqual(chest["sets"], 2)

    def test_new_session_resolves_from_repository_without_chat_history(self):
        resolved = MODULE.resolve_session("2026-10-06", "A", completed_as_prescribed=True)
        self.assertEqual(resolved["prescription_id"], "2026-08-31-baseline")
        self.assertEqual(resolved["trial_id"], "2026-10-04-A-upper-trial")
        lat = next(item for item in resolved["effective_execution"] if item["id"] == "lat_pulldown")
        self.assertEqual(lat["weight_kg"], 47)
        self.assertEqual(lat["provenance"]["weight_kg"], "active_one_session_trial")

    def test_new_trial_does_not_apply_to_its_source_session(self):
        resolved = MODULE.resolve_session("2026-10-04", "A", completed_as_prescribed=True)
        self.assertIsNone(resolved["trial_id"])
        lat = next(item for item in resolved["effective_execution"] if item["id"] == "lat_pulldown")
        self.assertEqual(lat["weight_kg"], 40)

    def test_trial_can_override_treadmill_steps_too(self):
        _, c_menu = MODULE.resolve_prescription(self.manifest, "2026-10-06", "C", "standard")
        effective = MODULE.interpret_execution(
            c_menu, completed_as_prescribed=True,
            trial_targets=[{"exercise_id": "treadmill_main", "fields": {"steps": [{"duration_min": 35, "speed_kmh": 6.0, "incline_percent": 7}]}}],
        )
        main = next(item for item in effective if item["id"] == "treadmill_main")
        self.assertEqual(main["steps"][0]["incline_percent"], 7)
        self.assertEqual(main["provenance"]["steps"], "active_one_session_trial")

    def test_active_trial_must_close_after_next_matching_session(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "data/logs/structured/sessions.csv"
            path.parent.mkdir(parents=True)
            path.write_text("date,session_type\n2026-10-06,A_full\n", encoding="utf-8")
            with self.assertRaises(MODULE.PrescriptionError):
                MODULE.validate_trial_lifecycle(self.trials, root)

    def test_one_set_can_change_without_replacing_workout(self):
        effective = MODULE.interpret_execution(
            self.a_menu, completed_as_prescribed=True,
            reported_deviations=[{"exercise_id": "seated_leg_press", "set_index": 3, "fields": {"actual_reps": 6}}],
        )
        leg = next(item for item in effective if item["id"] == "seated_leg_press")
        self.assertEqual(leg["set_overrides"]["3"]["actual_reps"]["value"], 6)
        self.assertEqual(leg["weight_kg"], 125)
        self.assertEqual(leg["sets"], 3)

    def test_skipped_exercise_does_not_delete_other_exercises(self):
        effective = MODULE.interpret_execution(
            self.a_menu, completed_as_prescribed=True,
            reported_deviations=[{"exercise_id": "chest_press", "fields": {"status": "skipped"}}],
        )
        values = {item["id"]: item for item in effective}
        self.assertEqual(values["chest_press"]["status"], "skipped")
        self.assertEqual(values["lat_pulldown"]["weight_kg"], 40)

    def test_missing_historical_prescription_fails_closed(self):
        with self.assertRaises(MODULE.PrescriptionError):
            MODULE.resolve_prescription(self.manifest, "2026-08-11", "A")

    def test_resolution_selects_snapshot_at_date_boundary_without_mutation(self):
        manifest = deepcopy(self.manifest)
        newer = deepcopy(manifest["snapshots"][0])
        newer.update(id="test-newer", effective_from="2026-10-10")
        leg = next(item for item in newer["menus"]["A"] if item["id"] == "seated_leg_press")
        leg["weight_kg"] = 130
        manifest["snapshots"].append(newer)
        before = deepcopy(manifest)
        old_id, _ = MODULE.resolve_prescription(manifest, "2026-10-09", "A")
        new_id, exercises = MODULE.resolve_prescription(manifest, "2026-10-10", "A")
        self.assertEqual(old_id, self.manifest["snapshots"][0]["id"])
        self.assertEqual(new_id, "test-newer")
        resolved_leg = next(item for item in exercises if item["id"] == "seated_leg_press")
        self.assertEqual(resolved_leg["weight_kg"], 130)
        resolved_leg["weight_kg"] = 999
        self.assertEqual(manifest, before)

    def test_unconfirmed_workout_cannot_inherit_all_exercises(self):
        with self.assertRaises(MODULE.PrescriptionError):
            MODULE.interpret_execution(self.a_menu, completed_as_prescribed=False)

    def test_duplicate_id_and_broken_source_hash_fail_validation(self):
        duplicate = deepcopy(self.manifest)
        duplicate["snapshots"].append(deepcopy(duplicate["snapshots"][0]))
        with self.assertRaises(MODULE.PrescriptionError):
            MODULE.validate_manifest(duplicate)
        broken = deepcopy(self.manifest)
        broken["snapshots"][0]["source_sha256"] = "bad"
        with self.assertRaises(MODULE.PrescriptionError):
            MODULE.validate_manifest(broken)

    def test_trial_display_change_does_not_change_base_prescription(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "data/menus/current-menus.md"
            source.parent.mkdir(parents=True)
            current_text = (ROOT / "data/menus/current-menus.md").read_text(encoding="utf-8")
            source.write_text(current_text.replace("次回Aだけ試行", "今回限り試行"), encoding="utf-8")
            MODULE.validate_manifest(self.manifest, root)
            source.write_text(current_text.replace("参考重量: 125kg", "参考重量: 115kg"), encoding="utf-8")
            with self.assertRaises(MODULE.PrescriptionError):
                MODULE.validate_manifest(self.manifest, root)

    def test_c_mode_is_required(self):
        with self.assertRaises(MODULE.PrescriptionError):
            MODULE.resolve_prescription(self.manifest, "2026-10-04", "C")


if __name__ == "__main__":
    unittest.main()

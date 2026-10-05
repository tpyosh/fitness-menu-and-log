#!/usr/bin/env python3
"""Resolve a dated workout prescription and apply observed execution deltas.

This module deliberately keeps an effective baseline separate from direct observations.
It never turns a prescribed rep range into an exact observed rep count.
"""

from __future__ import annotations

import hashlib
import json
import csv
import re
from copy import deepcopy
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PRESCRIPTIONS = ROOT / "data/menus/prescriptions.json"
TRIALS = ROOT / "data/menus/active-trials.json"
MACHINE_TITLES = {
    "Seated Leg Press": "seated_leg_press",
    "Seated Leg Curl": "seated_leg_curl",
    "Leg Extension": "leg_extension",
    "Lat Pulldown": "lat_pulldown",
    "Chest Press": "chest_press",
    "Hip Abduction (Outward / 外向き)": "hip_abduction_outward",
    "Abdominal": "abdominal",
    "Row Machine": "row_machine",
    "Shoulder Press": "shoulder_press",
    "Torso Rotation": "torso_rotation",
}


class PrescriptionError(ValueError):
    """A prescription cannot be resolved without inventing state."""


class ObservationConflict(ValueError):
    """Two direct observations disagree about the same execution field."""


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def baseline_menu_text(markdown: str) -> str:
    """Exclude transient next-session trial displays from the base menu hash."""
    return re.sub(r"^## 次回[^\n]*\n.*?(?=^## |^# |\Z)", "", markdown, flags=re.M | re.S)


def validate_manifest(manifest: dict[str, Any], root: Path = ROOT) -> None:
    if manifest.get("schema_version") != 1:
        raise PrescriptionError("Unsupported prescription schema_version")
    snapshots = manifest.get("snapshots")
    if not isinstance(snapshots, list) or not snapshots:
        raise PrescriptionError("No prescription snapshots")
    ids: set[str] = set()
    dates: set[str] = set()
    for snapshot in snapshots:
        identifier = snapshot["id"]
        effective_from = snapshot["effective_from"]
        date.fromisoformat(effective_from)
        if identifier in ids or effective_from in dates:
            raise PrescriptionError("Duplicate prescription id or effective_from")
        ids.add(identifier)
        dates.add(effective_from)
        menus = snapshot.get("menus", {})
        for menu in ("A", "B"):
            exercises = menus.get(menu)
            if not isinstance(exercises, list) or not exercises:
                raise PrescriptionError(f"Missing {menu} prescription")
            exercise_ids = [item["id"] for item in exercises]
            if len(exercise_ids) != len(set(exercise_ids)):
                raise PrescriptionError(f"Duplicate {menu} exercise id")
            for item in exercises:
                _validate_exercise(item)
        modes = menus.get("C", {})
        if set(modes) != {"recovery", "standard", "endurance"}:
            raise PrescriptionError("Missing C mode")
        for exercises in modes.values():
            for item in exercises:
                _validate_exercise(item)
    if manifest.get("current_id") not in ids:
        raise PrescriptionError("current_id does not name a snapshot")
    current = next(item for item in snapshots if item["id"] == manifest["current_id"])
    if current != max(snapshots, key=lambda item: item["effective_from"]):
        raise PrescriptionError("current_id is not the latest snapshot")
    source = root / current["source_file"]
    if not source.is_file():
        raise PrescriptionError(f"Current menu missing: {source}")
    source_text = source.read_text(encoding="utf-8")
    baseline_sha = hashlib.sha256(baseline_menu_text(source_text).encode("utf-8")).hexdigest()
    if baseline_sha != current["source_sha256"]:
        raise PrescriptionError("Current menu changed without a new prescription snapshot")
    validate_current_menu_values(source_text, current["menus"])


def validate_current_menu_values(markdown: str, menus: dict[str, Any]) -> None:
    """Check snapshot numbers against the human-readable latest menu."""
    for menu, following in (("A", "B"), ("B", "C")):
        section = markdown.split(f"# {menu}（", 1)[1].split(f"# {following}（", 1)[0]
        blocks = re.findall(r"^## [①-⑩]+ (.+?)\n(.*?)(?=^## |\Z)", section, re.M | re.S)
        actual: dict[str, tuple[float, int, int, int]] = {}
        for title, body in blocks:
            if title not in MACHINE_TITLES:
                continue
            weight = re.search(r"参考重量: ([\d.]+)kg", body)
            reps = re.search(r"(?:左右)?(\d+)〜(\d+)回 × (\d+)set", body)
            if not weight or not reps:
                raise PrescriptionError(f"Cannot parse {menu} {title}")
            actual[MACHINE_TITLES[title]] = (
                float(weight[1]), int(reps[1]), int(reps[2]), int(reps[3])
            )
        expected = {
            item["id"]: (float(item["weight_kg"]), item["reps_min"], item["reps_max"], item["sets"])
            for item in menus[menu] if item["kind"] == "machine"
        }
        if actual != expected:
            raise PrescriptionError(f"{menu} machine numbers differ from current-menus.md")
        warmup = next(item for item in menus[menu] if item["id"] == "warmup")
        main = next(item for item in menus[menu] if item["id"] == "treadmill_main")
        warmup_block = next(body for title, body in blocks if title.startswith("トレッドミル WU"))
        warmup_speed = warmup["steps"][0]["speed_kmh"]
        warmup_incline = warmup["steps"][0]["incline_percent"]
        if f"{warmup_speed:.1f} km/h・傾斜{warmup_incline}%" not in warmup_block:
            raise PrescriptionError(f"{menu} warmup differs from current-menus.md")
        main_block = next(body for title, body in blocks if title.startswith("トレッドミル（"))
        for step in main["steps"]:
            expected_line = f"{step['speed_kmh']:.1f} km/h・{step['incline_percent']}% × {step['duration_min']}分"
            if expected_line not in main_block:
                raise PrescriptionError(f"{menu} treadmill differs from current-menus.md")
    c_section = markdown.split("# C（", 1)[1]
    for mode, title in (("recovery", "Recovery"), ("standard", "Standard"), ("endurance", "Endurance")):
        block = c_section.split(f"## {title}（", 1)[1].split("\n## ", 1)[0]
        for exercise, label in zip(menus["C"][mode], ("ウォームアップ", "メイン", "クールダウン")):
            step = exercise["steps"][0]
            expected = (
                f"{label}{step['duration_min']}分: "
                f"{step['speed_kmh']:.1f} km/h・傾斜{step['incline_percent']}%"
            )
            if expected not in block:
                raise PrescriptionError(f"C {mode} differs from current-menus.md")


def _validate_exercise(item: dict[str, Any]) -> None:
    if item.get("kind") == "machine":
        required = ("weight_kg", "reps_min", "reps_max", "sets")
        if any(item.get(key) is None for key in required):
            raise PrescriptionError(f"Incomplete machine prescription: {item.get('id')}")
        if item["reps_min"] > item["reps_max"] or item["sets"] < 1:
            raise PrescriptionError(f"Invalid machine prescription: {item['id']}")
    elif item.get("kind") == "treadmill":
        steps = item.get("steps", [])
        if not steps or any(
            not all(key in step for key in ("duration_min", "speed_kmh", "incline_percent"))
            for step in steps
        ):
            raise PrescriptionError(f"Incomplete treadmill prescription: {item.get('id')}")
    else:
        raise PrescriptionError(f"Unknown exercise kind: {item.get('id')}")


def resolve_prescription(
    manifest: dict[str, Any], session_date: str, menu: str, c_mode: str | None = None
) -> tuple[str, list[dict[str, Any]]]:
    """Fail closed before the earliest snapshot or for an unknown menu/mode."""
    target = date.fromisoformat(session_date)
    eligible = [
        item for item in manifest["snapshots"]
        if date.fromisoformat(item["effective_from"]) <= target
    ]
    if not eligible:
        raise PrescriptionError(f"No prescription for {session_date}")
    snapshot = max(eligible, key=lambda item: item["effective_from"])
    menus = snapshot["menus"]
    if menu not in menus:
        raise PrescriptionError(f"Unknown menu: {menu}")
    if menu == "C":
        if c_mode not in menus["C"]:
            raise PrescriptionError("C mode is required")
        return snapshot["id"], deepcopy(menus["C"][c_mode])
    return snapshot["id"], deepcopy(menus[menu])


def validate_trials(trials: dict[str, Any], manifest: dict[str, Any]) -> None:
    if trials.get("schema_version") != 1:
        raise PrescriptionError("Unsupported trial schema_version")
    ids: set[str] = set()
    for trial in trials.get("trials", []):
        if trial["id"] in ids:
            raise PrescriptionError("Duplicate trial id")
        ids.add(trial["id"])
        if trial["status"] not in {"active", "completed", "declined", "expired"}:
            raise PrescriptionError("Unknown trial status")
        if trial["menu"] not in {"A", "B", "C"}:
            raise PrescriptionError("Unknown trial menu")
        _, exercises = resolve_prescription(
            manifest, trial["created_on"], trial["menu"], trial.get("c_mode")
        )
        exercise_ids = {item["id"] for item in exercises}
        for target in trial["targets"]:
            if target["exercise_id"] not in exercise_ids:
                raise PrescriptionError("Trial target not in prescription")
            exercise = next(item for item in exercises if item["id"] == target["exercise_id"])
            if not isinstance(target.get("fields"), dict) or not target["fields"]:
                raise PrescriptionError("Trial target has no fields")
            if not set(target["fields"]).issubset(exercise):
                raise PrescriptionError("Trial target has an unknown field")


def active_trials(trials: dict[str, Any], menu: str, session_date: str | None = None) -> list[dict[str, Any]]:
    return [
        item for item in trials["trials"]
        if item["menu"] == menu
        and item["status"] == "active"
        and (session_date is None or item["created_on"] < session_date)
    ]


def validate_trial_lifecycle(trials: dict[str, Any], root: Path = ROOT) -> None:
    """An active one-session trial must be closed after the next matching log."""
    with (root / "data/logs/structured/sessions.csv").open(encoding="utf-8", newline="") as stream:
        sessions = list(csv.DictReader(stream))
    for trial in trials["trials"]:
        if trial["status"] != "active":
            continue
        later_same_menu = [
            session for session in sessions
            if session["date"] > trial["created_on"]
            and session["session_type"].startswith(trial["menu"] + "_")
        ]
        if later_same_menu:
            raise PrescriptionError(f"Active trial must be closed after {later_same_menu[0]['date']}: {trial['id']}")


def interpret_execution(
    exercises: list[dict[str, Any]],
    *,
    completed_as_prescribed: bool,
    reported_deviations: list[dict[str, Any]] | None = None,
    observations: list[dict[str, Any]] | None = None,
    trial_targets: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Apply partial patches; direct observations override the inherited baseline.

    Each delta/observation has exercise_id and fields. A set_index (1-based) limits
    it to one prescribed set. Two direct sources disagreeing on one field fail closed.
    Garmin summary totals must not be mapped to per-exercise fields by the caller.
    """
    if not completed_as_prescribed:
        raise PrescriptionError("Completion is unknown; cannot inherit the full workout")
    result = []
    by_id: dict[str, dict[str, Any]] = {}
    for exercise in exercises:
        value = deepcopy(exercise)
        value["provenance"] = {key: "prescribed_no_deviation_reported" for key in value if key not in {"id", "kind", "provenance"}}
        value["direct_observations"] = {}
        value["set_overrides"] = {}
        result.append(value)
        by_id[value["id"]] = value
    for target in trial_targets or []:
        identifier = target["exercise_id"]
        if identifier not in by_id:
            raise PrescriptionError(f"Invalid trial target: {identifier}")
        for key, value in target["fields"].items():
            if key not in by_id[identifier] or key in {"id", "kind"}:
                raise PrescriptionError(f"Invalid trial field: {identifier}.{key}")
            by_id[identifier][key] = value
            by_id[identifier]["provenance"][key] = "active_one_session_trial"
    seen: dict[tuple[str, int | None, str], Any] = {}
    for source, patches in (("user_reported", reported_deviations or []), ("observed", observations or [])):
        for patch in patches:
            identifier = patch["exercise_id"]
            if identifier not in by_id:
                raise PrescriptionError(f"Unknown exercise in execution: {identifier}")
            item = by_id[identifier]
            set_index = patch.get("set_index")
            if set_index is not None and (item["kind"] != "machine" or not 1 <= set_index <= item["sets"]):
                raise PrescriptionError("Invalid set_index")
            for key, value in patch["fields"].items():
                if key in {"id", "kind", "provenance"}:
                    raise PrescriptionError(f"Cannot override {key}")
                marker = (identifier, set_index, key)
                if marker in seen and seen[marker] != value:
                    raise ObservationConflict(f"Conflicting observations for {identifier}.{key}")
                seen[marker] = value
                if set_index is None:
                    if key not in item and key not in {"status", "actual_reps", "actual_duration_min"}:
                        raise PrescriptionError(f"Unknown execution field: {key}")
                    item[key] = value
                    item["provenance"][key] = source
                else:
                    item["set_overrides"].setdefault(str(set_index), {})[key] = {"value": value, "provenance": source}
                item["direct_observations"].setdefault(source, []).append({"field": key, "value": value, "set_index": set_index})
    return result


def resolve_session(
    session_date: str,
    menu: str,
    *,
    completed_as_prescribed: bool,
    reported_deviations: list[dict[str, Any]] | None = None,
    observations: list[dict[str, Any]] | None = None,
    c_mode: str | None = None,
    root: Path = ROOT,
) -> dict[str, Any]:
    manifest = load_json(root / "data/menus/prescriptions.json")
    validate_manifest(manifest, root)
    prescription_id, exercises = resolve_prescription(manifest, session_date, menu, c_mode)
    trials = load_json(root / "data/menus/active-trials.json")
    validate_trials(trials, manifest)
    validate_trial_lifecycle(trials, root)
    applicable = active_trials(trials, menu, session_date)
    if len(applicable) > 1:
        raise PrescriptionError(f"Multiple active trials for {menu}")
    trial = applicable[0] if applicable else None
    return {
        "prescription_id": prescription_id,
        "trial_id": trial["id"] if trial else None,
        "menu": menu,
        "c_mode": c_mode,
        "effective_execution": interpret_execution(
            exercises,
            completed_as_prescribed=completed_as_prescribed,
            reported_deviations=reported_deviations,
            observations=observations,
            trial_targets=trial["targets"] if trial else None,
        ),
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Resolve a dated menu and observed deltas")
    parser.add_argument("--date", required=True)
    parser.add_argument("--menu", required=True, choices=("A", "B", "C"))
    parser.add_argument("--c-mode", choices=("recovery", "standard", "endurance"))
    parser.add_argument("--completed", action="store_true", help="User reported completing this menu")
    parser.add_argument("--deviations-json", default="[]", help="JSON list of user reported exercise patches")
    parser.add_argument("--observations-json", default="[]", help="JSON list of direct observed exercise patches")
    args = parser.parse_args()
    resolved = resolve_session(
        args.date,
        args.menu,
        c_mode=args.c_mode,
        completed_as_prescribed=args.completed,
        reported_deviations=json.loads(args.deviations_json),
        observations=json.loads(args.observations_json),
    )
    print(json.dumps(resolved, ensure_ascii=False, indent=2))

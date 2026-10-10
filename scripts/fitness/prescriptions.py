"""Validate and resolve versioned prescriptions and one-session trials."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from copy import deepcopy
from datetime import date
from pathlib import Path
from typing import Any

from .paths import ROOT


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


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def baseline_menu_text(markdown: str) -> str:
    """Exclude transient next-session trial displays from the base menu hash."""
    markdown = re.sub(
        r"^<!-- next-session-trial:start -->\n.*?^<!-- next-session-trial:end -->\n?",
        "", markdown, flags=re.M | re.S,
    )
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

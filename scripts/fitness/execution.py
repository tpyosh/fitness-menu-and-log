"""Combine prescriptions, active trials, reported deltas, and observations."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from .paths import ROOT
from .prescriptions import (
    PrescriptionError,
    active_trials,
    load_json,
    resolve_prescription,
    validate_manifest,
    validate_trial_lifecycle,
    validate_trials,
)


class ObservationConflict(ValueError):
    """Two direct observations disagree about the same execution field."""


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

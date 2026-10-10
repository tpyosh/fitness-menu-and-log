#!/usr/bin/env python3
"""Resolve a dated workout prescription and apply observed execution deltas.

The public helpers remain available here for existing callers. Their implementation
lives in fitness.prescriptions and fitness.execution.
"""

from __future__ import annotations

import argparse
import json

if __package__:
    from .fitness.execution import ObservationConflict, interpret_execution, resolve_session
    from .fitness.paths import PRESCRIPTIONS, ROOT, TRIALS
    from .fitness.prescriptions import (
        MACHINE_TITLES,
        PrescriptionError,
        active_trials,
        baseline_menu_text,
        load_json,
        resolve_prescription,
        validate_current_menu_values,
        validate_manifest,
        validate_trial_lifecycle,
        validate_trials,
    )
else:
    from fitness.execution import ObservationConflict, interpret_execution, resolve_session
    from fitness.paths import PRESCRIPTIONS, ROOT, TRIALS
    from fitness.prescriptions import (
        MACHINE_TITLES,
        PrescriptionError,
        active_trials,
        baseline_menu_text,
        load_json,
        resolve_prescription,
        validate_current_menu_values,
        validate_manifest,
        validate_trial_lifecycle,
        validate_trials,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve a dated menu and observed deltas")
    parser.add_argument("--date", required=True)
    parser.add_argument("--menu", required=True, choices=("A", "B", "C"))
    parser.add_argument("--c-mode", choices=("recovery", "standard", "endurance"))
    parser.add_argument("--completed", action="store_true", help="User reported completing this menu")
    parser.add_argument("--deviations-json", default="[]", help="JSON list of user reported exercise patches")
    parser.add_argument("--observations-json", default="[]", help="JSON list of direct observed exercise patches")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    resolved = resolve_session(
        args.date,
        args.menu,
        c_mode=args.c_mode,
        completed_as_prescribed=args.completed,
        reported_deviations=json.loads(args.deviations_json),
        observations=json.loads(args.observations_json),
    )
    print(json.dumps(resolved, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

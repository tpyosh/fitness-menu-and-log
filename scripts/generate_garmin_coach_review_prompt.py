#!/usr/bin/env python3
"""Generate an on-demand Garmin coaching review prompt."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

if __package__:
    from .fitness.paths import (
        CURRENT_MENUS,
        DESIGN_PHILOSOPHY,
        HISTORY_PATH,
        PROMPT_TEMPLATE,
        REVIEWS_DIR,
        ROOT,
        SESSIONS_CSV,
        SESSIONS_YAML,
        rel,
    )
    from .fitness.review_data import (
        choose_output_path,
        git_state,
        latest_history_record,
        load_history,
        load_sessions,
        load_yaml_details,
        load_yaml_excerpt_details,
        parse_record_date,
        parse_requested_at,
        parse_session_date,
        read_markdown,
        source_files,
    )
    from .fitness.review_rendering import (
        float_value,
        format_session,
        non_empty,
        range_text,
        render_prompt as _render_prompt,
        summarize_period,
        value,
    )
else:
    from fitness.paths import (
        CURRENT_MENUS,
        DESIGN_PHILOSOPHY,
        HISTORY_PATH,
        PROMPT_TEMPLATE,
        REVIEWS_DIR,
        ROOT,
        SESSIONS_CSV,
        SESSIONS_YAML,
        rel,
    )
    from fitness.review_data import (
        choose_output_path,
        git_state,
        latest_history_record,
        load_history,
        load_sessions,
        load_yaml_details,
        load_yaml_excerpt_details,
        parse_record_date,
        parse_requested_at,
        parse_session_date,
        read_markdown,
        source_files,
    )
    from fitness.review_rendering import (
        float_value,
        format_session,
        non_empty,
        range_text,
        render_prompt as _render_prompt,
        summarize_period,
        value,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a ChatGPT prompt for an on-demand Garmin coaching review."
    )
    parser.add_argument(
        "--requested-at",
        help="ISO timestamp for the request. Defaults to current local time.",
    )
    parser.add_argument(
        "--notes",
        default="",
        help="Optional freeform notes to include in the history record and prompt.",
    )
    parser.add_argument(
        "--baseline-sessions",
        type=int,
        default=3,
        help="Number of sessions before the previous review request to include as context.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output Markdown path. Defaults to data/logs/reviews/YYYY-MM-DD_garmin-coach-review-request.md.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the prompt without writing a request file or appending history.",
    )
    return parser.parse_args(argv)


def render_prompt(
    requested_at: datetime,
    previous_record: dict[str, Any] | None,
    target_sessions: list[dict[str, str]],
    baseline_sessions: list[dict[str, str]],
    details: dict[tuple[str, str], dict[str, Any]],
    notes: str,
) -> str:
    return _render_prompt(
        requested_at, previous_record, target_sessions, baseline_sessions, details, notes,
        design_philosophy=read_markdown(DESIGN_PHILOSOPHY),
        current_menus=read_markdown(CURRENT_MENUS),
        sources=source_files(),
    )


def build_record(
    requested_at: datetime,
    previous_record: dict[str, Any] | None,
    target_sessions: list[dict[str, str]],
    output_path: Path,
    notes: str,
) -> dict[str, Any]:
    if target_sessions:
        log_range = {
            "from": parse_session_date(target_sessions[0]).isoformat(),
            "to": parse_session_date(target_sessions[-1]).isoformat(),
            "session_count": len(target_sessions),
        }
    else:
        log_range = {"from": None, "to": None, "session_count": 0}
    return {
        "requested_at": requested_at.isoformat(),
        "timestamp_precision": "second",
        "repo_state": git_state(),
        "previous_review_requested_at": (
            previous_record.get("requested_at") if previous_record else None
        ),
        "log_range_covered": log_range,
        "files_used": source_files(),
        "prompt_file": rel(output_path),
        "short_summary": summarize_period(target_sessions),
        "notes": notes,
    }


def append_history(record: dict[str, Any]) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with HISTORY_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    requested_at = parse_requested_at(args.requested_at)
    history = load_history()
    previous_record = latest_history_record(history)
    previous_date = parse_record_date(str(previous_record.get("requested_at"))) if previous_record else None
    sessions = load_sessions()
    current_date = requested_at.date()

    if previous_date:
        target_sessions = [
            row
            for row in sessions
            if previous_date < parse_session_date(row) <= current_date
        ]
        baseline_pool = [
            row
            for row in sessions
            if parse_session_date(row) <= previous_date
        ]
    else:
        target_sessions = [row for row in sessions if parse_session_date(row) <= current_date]
        baseline_pool = []

    baseline_sessions = baseline_pool[-max(args.baseline_sessions, 0) :]
    details = load_yaml_details()
    output_path = choose_output_path(requested_at, args.output)
    prompt = render_prompt(
        requested_at=requested_at,
        previous_record=previous_record,
        target_sessions=target_sessions,
        baseline_sessions=baseline_sessions,
        details=details,
        notes=args.notes,
    )
    record = build_record(
        requested_at=requested_at,
        previous_record=previous_record,
        target_sessions=target_sessions,
        output_path=output_path,
        notes=args.notes,
    )

    if args.dry_run:
        print(prompt)
        print("\n--- dry-run history record ---", file=sys.stderr)
        print(json.dumps(record, ensure_ascii=False, indent=2), file=sys.stderr)
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(prompt, encoding="utf-8")
    append_history(record)
    print(f"Wrote prompt: {rel(output_path)}")
    print(f"Appended history: {rel(HISTORY_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

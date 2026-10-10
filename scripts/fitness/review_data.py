"""Read review history and session sources without modifying training records."""

from __future__ import annotations

import csv
import json
import subprocess
from datetime import date, datetime
from pathlib import Path
from typing import Any

from .paths import (
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


def parse_requested_at(value: str | None) -> datetime:
    if not value:
        return datetime.now().astimezone().replace(microsecond=0)
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise SystemExit(f"Invalid --requested-at value: {value}") from exc
    if isinstance(parsed, datetime):
        return parsed.replace(microsecond=0)
    raise SystemExit(f"Invalid --requested-at value: {value}")


def parse_record_date(value: str | None) -> date | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized).date()
    except ValueError:
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None


def parse_session_date(row: dict[str, str]) -> date:
    try:
        return date.fromisoformat(row["date"])
    except (KeyError, ValueError) as exc:
        raise SystemExit(f"Invalid session date in {rel(SESSIONS_CSV)}: {row}") from exc


def load_history() -> list[dict[str, Any]]:
    if not HISTORY_PATH.exists():
        return []
    records: list[dict[str, Any]] = []
    with HISTORY_PATH.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                records.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise SystemExit(
                    f"Invalid JSONL at {rel(HISTORY_PATH)}:{line_number}"
                ) from exc
    return records


def latest_history_record(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    dated_records = [
        (parse_record_date(str(record.get("requested_at", ""))), record)
        for record in records
    ]
    dated_records = [(record_date, record) for record_date, record in dated_records if record_date]
    if not dated_records:
        return None
    return sorted(dated_records, key=lambda item: item[0])[-1][1]


def load_sessions() -> list[dict[str, str]]:
    with SESSIONS_CSV.open(encoding="utf-8", newline="") as file:
        sessions = list(csv.DictReader(file))
    return sorted(sessions, key=parse_session_date)


def load_yaml_details() -> dict[tuple[str, str], dict[str, Any]]:
    try:
        import yaml  # type: ignore
    except ImportError:
        return load_yaml_excerpt_details()

    if not SESSIONS_YAML.exists():
        return {}
    with SESSIONS_YAML.open(encoding="utf-8") as file:
        loaded = yaml.safe_load(file) or {}
    details: dict[tuple[str, str], dict[str, Any]] = {}
    for session in loaded.get("sessions", []):
        key = (str(session.get("date", "")), str(session.get("session_type", "")))
        details[key] = session
    return details


def load_yaml_excerpt_details() -> dict[tuple[str, str], dict[str, Any]]:
    if not SESSIONS_YAML.exists():
        return {}
    lines = SESSIONS_YAML.read_text(encoding="utf-8").splitlines()
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if line.startswith("  - date: "):
            if current:
                blocks.append(current)
            current = [line]
        elif current:
            current.append(line)
    if current:
        blocks.append(current)

    details: dict[tuple[str, str], dict[str, Any]] = {}
    for block in blocks:
        date_text = ""
        session_type = ""
        for line in block:
            stripped = line.strip()
            if stripped.startswith("- date: "):
                date_text = stripped.split(": ", 1)[1].strip().strip('"')
            elif stripped.startswith("session_type: "):
                session_type = stripped.split(": ", 1)[1].strip().strip('"')
            if date_text and session_type:
                break
        if date_text and session_type:
            details[(date_text, session_type)] = {
                "raw_yaml_excerpt": "\n".join(block),
            }
    return details


def git_state() -> str:
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        status = subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=ROOT,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except subprocess.CalledProcessError:
        return "unknown"
    return f"{commit}+dirty" if status.strip() else commit


def read_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def choose_output_path(requested_at: datetime, explicit: Path | None) -> Path:
    if explicit:
        return explicit if explicit.is_absolute() else ROOT / explicit
    base = REVIEWS_DIR / f"{requested_at.date().isoformat()}_garmin-coach-review-request.md"
    if not base.exists():
        return base
    suffix = requested_at.strftime("%H%M%S")
    return REVIEWS_DIR / f"{requested_at.date().isoformat()}_{suffix}_garmin-coach-review-request.md"


def source_files() -> list[str]:
    return [
        rel(SESSIONS_CSV),
        rel(SESSIONS_YAML),
        rel(CURRENT_MENUS),
        rel(DESIGN_PHILOSOPHY),
        rel(PROMPT_TEMPLATE),
        rel(HISTORY_PATH),
    ]

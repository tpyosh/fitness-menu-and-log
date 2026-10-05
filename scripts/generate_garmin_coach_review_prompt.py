#!/usr/bin/env python3
"""Generate an on-demand Garmin coaching review prompt."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HISTORY_PATH = ROOT / "data/logs/reviews/review-request-history.jsonl"
SESSIONS_CSV = ROOT / "data/logs/structured/sessions.csv"
SESSIONS_YAML = ROOT / "data/logs/structured/sessions.yaml"
CURRENT_MENUS = ROOT / "data/menus/current-menus.md"
DESIGN_PHILOSOPHY = ROOT / "data/menus/design-philosophy.md"
PROMPT_TEMPLATE = ROOT / "data/prompts/garmin-coach-review-request.md"
REVIEWS_DIR = ROOT / "data/logs/reviews"


def parse_args() -> argparse.Namespace:
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
    return parser.parse_args()


def rel(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return str(resolved)


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


def non_empty(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def value(row: dict[str, str], key: str) -> str:
    raw = row.get(key, "")
    return raw if non_empty(raw) else "unknown"


def float_value(row: dict[str, str], key: str) -> float | None:
    raw = row.get(key, "")
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def range_text(values: list[float]) -> str:
    if not values:
        return "unknown"
    return f"{min(values):g}-{max(values):g}"


def summarize_period(sessions: list[dict[str, str]]) -> str:
    if not sessions:
        return "対象ログ0件。前回レビュー依頼以降の新規Garminログは見つかりませんでした。"
    first = parse_session_date(sessions[0]).isoformat()
    last = parse_session_date(sessions[-1]).isoformat()
    type_counts = Counter(value(row, "session_type") for row in sessions)
    type_text = ", ".join(f"{session_type} x {count}" for session_type, count in type_counts.items())
    avg_hr = [number for row in sessions if (number := float_value(row, "avg_hr")) is not None]
    max_hr = [number for row in sessions if (number := float_value(row, "max_hr")) is not None]
    aerobic_te = [number for row in sessions if (number := float_value(row, "aerobic_te")) is not None]
    exercise_load = [number for row in sessions if (number := float_value(row, "exercise_load")) is not None]
    load_text = f", exercise_load合計 {sum(exercise_load):g}" if exercise_load else ""
    if first == last:
        range_part = first
    else:
        range_part = f"{first} から {last}"
    return (
        f"対象ログ{len(sessions)}件 ({range_part})。"
        f"内訳: {type_text}。"
        f"Avg HR範囲 {range_text(avg_hr)}, Max HR範囲 {range_text(max_hr)}, "
        f"Aerobic TE範囲 {range_text(aerobic_te)}{load_text}。"
    )


def format_session(row: dict[str, str], details: dict[tuple[str, str], dict[str, Any]]) -> str:
    date_text = value(row, "date")
    session_type = value(row, "session_type")
    key = (date_text, session_type)
    detail = details.get(key, {})
    lines = [
        f"### {date_text} {session_type}",
        "",
        "- Summary:",
        f"  - duration_min: {value(row, 'duration_min')}",
        f"  - avg_hr: {value(row, 'avg_hr')}",
        f"  - max_hr: {value(row, 'max_hr')}",
        f"  - aerobic_te: {value(row, 'aerobic_te')}",
        f"  - anaerobic_te: {value(row, 'anaerobic_te')}",
        f"  - exercise_load: {value(row, 'exercise_load')}",
        f"  - calories: {value(row, 'calories')}",
        f"  - primary_benefit: {value(row, 'primary_benefit')}",
        f"  - zone1_time: {value(row, 'zone1_time')}",
        f"  - zone2_time: {value(row, 'zone2_time')}",
        f"  - zone3_time: {value(row, 'zone3_time')}",
        f"  - zone4_time: {value(row, 'zone4_time')}",
        f"  - zone5_time: {value(row, 'zone5_time')}",
        f"  - subjective_fatigue: {value(row, 'subjective_fatigue')}",
        f"  - soreness_next_day: {value(row, 'soreness_next_day')}",
        f"  - menu_deviation: {value(row, 'menu_deviation')}",
        f"  - notes: {value(row, 'notes')}",
    ]
    segments = detail.get("segments", [])
    if segments:
        lines.extend(["", "- Segments from sessions.yaml:"])
        for segment in segments:
            segment_line = (
                f"  - {segment.get('segment_type', 'unknown')}: "
                f"duration_min={segment.get('duration_min', 'unknown')}, "
                f"avg_hr={segment.get('avg_hr', 'unknown')}, "
                f"max_hr={segment.get('max_hr', 'unknown')}, "
                f"calories={segment.get('calories', 'unknown')}"
            )
            if non_empty(segment.get("notes")):
                segment_line += f", notes={segment.get('notes')}"
            lines.append(segment_line)
    machine_adjustments = detail.get("machine_adjustments", [])
    if machine_adjustments:
        lines.extend(["", "- Machine adjustments from sessions.yaml:"])
        for adjustment in machine_adjustments:
            lines.append(
                "  - "
                + ", ".join(
                    f"{key}={adjustment.get(key, 'unknown')}"
                    for key in [
                        "machine",
                        "planned_weight_kg",
                        "actual_weight_kg",
                        "adjustment",
                        "resolution_basis",
                        "subjective_comment",
                    ]
                )
            )
    if detail.get("prescription_id"):
        lines.append(f"- Prescription id: {detail['prescription_id']}")
    for field in ("prescribed_workout", "reported_deviations", "effective_execution"):
        if field in detail:
            lines.append(f"- {field}: {json.dumps(detail[field], ensure_ascii=False, default=str)}")
    raw_yaml_excerpt = detail.get("raw_yaml_excerpt")
    if raw_yaml_excerpt and not segments:
        lines.extend(["", "- Raw sessions.yaml excerpt:", "```yaml", str(raw_yaml_excerpt), "```"])
    return "\n".join(lines)


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


def render_prompt(
    requested_at: datetime,
    previous_record: dict[str, Any] | None,
    target_sessions: list[dict[str, str]],
    baseline_sessions: list[dict[str, str]],
    details: dict[tuple[str, str], dict[str, Any]],
    notes: str,
) -> str:
    previous_requested_at = (
        str(previous_record.get("requested_at"))
        if previous_record and previous_record.get("requested_at")
        else "なし"
    )
    if target_sessions:
        data_range = (
            f"{parse_session_date(target_sessions[0]).isoformat()} から "
            f"{parse_session_date(target_sessions[-1]).isoformat()}"
        )
    else:
        data_range = "前回レビュー依頼以降の新規ログなし"
    target_text = (
        "\n\n".join(format_session(row, details) for row in target_sessions)
        if target_sessions
        else "前回レビュー依頼以降の新規Garminログはありません。変更提案を作る前に、データ不足として扱ってください。"
    )
    baseline_text = (
        "\n\n".join(format_session(row, details) for row in baseline_sessions)
        if baseline_sessions
        else "利用できるベースライン文脈はありません。"
    )
    notes_text = notes if notes else "追加メモなし"
    source_files_text = "\n".join(f"  - {item}" for item in source_files())

    return f"""# ChatGPT Garmin Coaching Review Request

以下は、現在運用しているフィットネスメニュー管理情報とGarminログです。
必要であればメニューを修正してください。
ただし、レビュー依頼があるだけで改善案を作らないでください。

重要原則:

> Do not assume that every review request requires an improvement proposal. If the recent logs show stable, appropriate, or insufficiently informative data, say so. A valid output may be: continue current plan, monitor specific indicators, and make no menu change.

日本語でも同じ方針で判断してください。直近ログが安定、適切、または判断材料不足なら、「現行継続」「特定指標の監視」「メニュー変更なし」を有効な結論として扱ってください。

# 1. レビュー範囲

- Last review request: {previous_requested_at}
- Current review request: {requested_at.isoformat()}
- Data range: {data_range}
- Source files used:
{source_files_text}
- Request notes: {notes_text}

# 2. データ品質 / 制約

- Garminログは、リポジトリ内のCSV/YAMLに記録済みの値だけを使ってください
- 不明値は `unknown` として扱い、推測で補完しないでください
- Garminにはマシンごとの全セット実績が残らない場合があります
- セッション件数が少ない場合、トレンドは弱い証拠として扱ってください
- 医療診断はしないでください

# 3. 現在の設計思想

{read_markdown(DESIGN_PHILOSOPHY)}

# 4. 現在のA/B/Cメニュー

{read_markdown(CURRENT_MENUS)}

# 5. 前回レビュー依頼以降の対象ログ

## 抽出期間サマリー

{summarize_period(target_sessions)}

{target_text}

# 6. 比較用ベースライン文脈

以下は、今回対象期間だけで判断が狭くなりすぎないように添える直前ログです。主対象ではなく、比較用として扱ってください。

## ベースラインサマリー

{summarize_period(baseline_sessions)}

{baseline_text}

# 7. 評価してほしいこと

- 前回レビュー依頼以降の変化を主対象として評価してください
- 必要に応じて、直近以前のベースラインと比較してください
- トレーニング量、強度、ペース、心拍、回復、継続性、疲労兆候のトレンドを見てください
- ただし、利用可能データで支えられる範囲だけを評価してください
- A日/B日の現行設計思想に照らして、狙い通りか見てください
- メニュー改善は、明確な理由がある場合だけ提案してください
- 観察事実、合理的解釈、不確かな仮説を分けてください
- 医療診断は避けてください
- 質問は、どうしても必要な場合だけにしてください。それ以外は仮定を明示してベストエフォートで返してください
- 出力は日本語にしてください

# 8. あなたの出力形式

以下の形式で返してください。

```md
# Garmin Coaching Review

## 1. Scope of review

- Last review request:
- Current review request:
- Data range:
- Data quality / limitations:

## 2. Observed changes since last review

Separate objective observations from interpretation.

## 3. Recent trend assessment

Discuss only supported trends.

## 4. Coaching judgment

Choose one:

- No change recommended
- Minor adjustment recommended
- Clear menu change recommended
- Insufficient data

## 5. Suggested training menu changes, if any

Only include if justified by the data.

## 6. Watch items until next review

List measurable indicators to monitor.

## 7. Codex handoff prompt

Write a concise prompt that I can paste back into Codex to apply any justified changes to this repository.
If no repository change is needed, the prompt should explicitly say that no menu change is recommended and only the review result should be recorded if the repo supports that.
```
"""


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


def main() -> int:
    args = parse_args()
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

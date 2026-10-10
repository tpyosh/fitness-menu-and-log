"""Render review summaries and prompts from supplied source text and records."""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from typing import Any

from .review_data import parse_session_date


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


def render_prompt(
    requested_at: datetime,
    previous_record: dict[str, Any] | None,
    target_sessions: list[dict[str, str]],
    baseline_sessions: list[dict[str, str]],
    details: dict[tuple[str, str], dict[str, Any]],
    notes: str,
    *,
    design_philosophy: str,
    current_menus: str,
    sources: list[str],
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
    source_files_text = "\n".join(f"  - {item}" for item in sources)

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

{design_philosophy}

# 4. 現在のA/B/Cメニュー

{current_menus}

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

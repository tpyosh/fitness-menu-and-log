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
    current_assessment: str,
    backlog: str,
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
本文完結型です。本文だけを新規ChatGPTチャットへ貼り付けて使います。パスは由来を示すもので、ローカルファイルの閲覧や添付を前提にしないでください。
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
- 本人申告・Garmin観測・処方継承・レビュー上の推論を区別してください

# 現在の判断と未解決課題（正本の本文）

## data/logs/reviews/current-assessment.md

{current_assessment}

## data/logs/reviews/backlog.md

{backlog}

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
- 判断に必要な情報が欠ける場合は未確認のまま残し、次に必要な確認を示してください。推測で実績を埋めないでください
- 出力は日本語にしてください

# 8. あなたの出力形式

今回実行するのは最初の一工程だけです。Request notesで指定された一論点を優先し、指定がなければバックログのP1から一論点を選びます。全課題の調査や最終成果物の同時作成は行わないでください。

今回の回答は、対象のJ/B-ID、結論、確認済み事実と根拠、推論、未確認事項、次に送る短い指示だけを簡潔に返してください。外部資料を確認した場合は出典名・直接URL・確認日・情報の変動性・適用限界を記録し、未確認の資料を確認済みにしないでください。

次工程はユーザが同じ会話で明示的に依頼してから実行してください。複数論点は一論点ずつ扱い、統合は確認済み情報だけで別工程にします。最後のCodex向け反映依頼も統合後の単独工程とします。

最終出力は、Codexへそのまま渡せる本文完結型のドキュメンテーション依頼プロンプトにしてください。目的・対象範囲・基準日・結論、事実／推論／未確認、直接URL等の出典情報、セッション・処方・試行IDと既存状態、J/B-IDごとの更新・維持・解決案を本文に含めてください。

反映先は`data/logs/reviews/current-assessment.md`と`data/logs/reviews/backlog.md`です。既存IDを更新し、同じ問いを重複作成せず、日付付きのレビュー回答・採否メモ・統合記録は作成しないよう指定してください。課題の解決には根拠と解決条件の成立が必要です。

既存スキーマ・命名・provenance・推測禁止・未確認を解決済みにしない条件、通常処方と次回試行の区別、変更禁止事項も含めてください。必要なYAML/JSON parse・ID重複・参照・本文ハッシュ検証、`ruby scripts/validate_fitness_data.rb`、コード変更時の既存テストを指定し、完了時は変更ファイル・反映内容・未解決事項・検証結果を報告させてください。
"""

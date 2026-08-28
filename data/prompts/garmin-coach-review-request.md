# Garmin Coach Review Request Template

このテンプレートは、CodexがオンデマンドのGarminコーチングレビュー依頼文を作るためのものです。目的は、前回レビュー依頼以降のログ変化を中心に見てもらい、根拠の薄いメニュー変更を防ぐことです。

## Codexの作業手順

1. `data/logs/reviews/review-request-history.jsonl` から直近のレビュー依頼を確認する
2. `data/logs/structured/sessions.csv` と `data/logs/structured/sessions.yaml` から、直近レビュー依頼以降のGarminログを抽出する
3. データ件数が少ない場合は、直近レビュー依頼以前の近いログをベースライン文脈として併記する
4. `data/menus/current-menus.md` と `data/menus/design-philosophy.md` を添付する
5. 新しいレビュー依頼のメタデータを `data/logs/reviews/review-request-history.jsonl` に追記する
6. ChatGPTへ貼るレビュー依頼文を `data/logs/reviews/YYYY-MM-DD_garmin-coach-review-request.md` に保存する

自動生成する場合は、以下を使う。

```sh
python3 scripts/generate_garmin_coach_review_prompt.py
```

内容確認だけなら、履歴を更新せずに以下を使う。

```sh
python3 scripts/generate_garmin_coach_review_prompt.py --dry-run
```

## ChatGPTへ依頼する内容

生成するChatGPT向けプロンプトには、少なくとも以下を含める。

- 現在の設計思想
- 現在のA60 / B60メニュー
- 現在のレビュー依頼日時
- 前回レビュー依頼日時
- レビュー対象のログ範囲
- 直近レビュー依頼以降の対象ログ
- 必要な場合のみ、前回レビュー依頼以前の近いベースラインログ
- データ品質上の制約
- ユーザ主観、メニュー逸脱、マシン重量変更が記録されている場合はその内容
- ヒップ系マシンは、内向き `hip_adduction_inward` と外向き `hip_abduction_outward` を別種目として比較する
- 「必要であればメニューを修正してください」という依頼

## 重要な反バイアス原則

ChatGPT向けプロンプトには、以下の原則を強く含める。

> Do not assume that every review request requires an improvement proposal. If the recent logs show stable, appropriate, or insufficiently informative data, say so. A valid output may be: continue current plan, monitor specific indicators, and make no menu change.

日本語でも同じ趣旨を明記する。

- レビュー依頼があるだけで改善案を作らない
- データが安定、適切、不十分な場合はそう書く
- 「現行継続」「特定指標の監視」「メニュー変更なし」を有効な結論として扱う
- Garmin指標だけで筋トレメニューを過剰に変えない
- 医療診断をしない

## ChatGPTへの評価依頼

ChatGPTには以下を依頼する。

- 前回レビュー依頼以降の変化を主対象にする
- 必要に応じて、直近以前のベースラインと比較する
- トレーニング量、強度、ペース、心拍、回復、継続性、疲労兆候のトレンドを評価する
- ただし、利用可能データで支えられる範囲だけを評価する
- メニュー改善は、明確な理由がある場合だけ提案する
- 「意味のある変更なし」を有効な結論にする
- 観察事実、合理的解釈、不確かな仮説を分ける
- 医療診断を避ける
- どうしても必要な場合だけ質問し、それ以外は仮定を明示してベストエフォートで返す
- 日本語で出力する

## ChatGPT出力形式

生成するレビュー依頼文では、ChatGPTに以下の形式で出力させる。

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

## 注意

- Garminログや主観メモを推測で補完しない
- セッション件数が少ないときは、トレンド断定を避ける
- 単発の重量変更だけで現行メニュー本体を更新する前提にしない
- ChatGPTは外部レビュアーであり、提案をそのまま正解扱いしない

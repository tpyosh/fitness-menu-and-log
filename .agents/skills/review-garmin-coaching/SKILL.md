---
name: review-garmin-coaching
description: ChatGPTへのGarminコーチングレビュー依頼、返却レビューの根拠確認、現在の判断と課題バックログの継続更新に使う。通常の単一セッション取り込みには使わない。
---

# Garminコーチングレビュー

外部レビューは複数ログの再評価として扱う。結果は[現在の判断](../../../data/logs/reviews/current-assessment.md)と[課題バックログ](../../../data/logs/reviews/backlog.md)の2つをSSOTとして更新する。

## 依頼を作る

1. [運用規約](../../../data/logs/reviews/README.md)、2つの正本、現行メニューと設計思想を読む。
2. [依頼テンプレート](../../../data/prompts/garmin-coach-review-request.md)に従い、`python3 scripts/generate_garmin_coach_review_prompt.py`で本文完結型の依頼文と最新メタデータを生成する。内容確認だけなら`--dry-run`。固定ファイルを更新し、日付付き依頼を増やさない。
3. 本文に現在の判断、バックログ、対象ログ、ユーザー主観、不確実性、最終Codex依頼の要件が含まれることを確認する。長い調査は一論点ずつ、統合と最終依頼は別工程にする。

## 回答を反映判断する

1. [回答反映テンプレート](../../../data/prompts/apply-garmin-coach-feedback.md)を読み、提案ごとに確認済み事実・推論・未確認事項を分け、処方とログに照合する。
2. 既存J-IDの判断・根拠・再検討条件を更新する。未解決の問いは既存B-IDへ統合し、次の確認と解決条件を更新する。新しい問いだけ新規IDを付ける。
3. 変更不要・根拠不足も有効な結論。未確認を解決済みにせず、解決には根拠を残す。回答全文、日付付き採否メモ、工程別・統合スナップショットは保存しない。
4. 採用する具体的な恒久改定だけ`$revise-training-menu`へ渡す。通常処方・次回試行・過去ログの正本との整合を検証する。

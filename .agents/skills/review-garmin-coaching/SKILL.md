---
name: review-garmin-coaching
description: ChatGPTへGarminコーチングレビューを依頼する、または返却済みレビューを根拠確認のうえ保存・反映判断するときに使う。通常の単一セッション取り込みには使わない。
---

# Garminコーチングレビュー

外部レビューは、通常のログ取り込みを補う複数ログの再評価として扱う。

## 依頼を作る

1. [レビュー依頼テンプレート](../../../data/prompts/garmin-coach-review-request.md)、[レビュー保存規約](../../../data/logs/reviews/README.md)、現行メニュー、設計思想を確認する。
2. `python3 scripts/generate_garmin_coach_review_prompt.py` を使って依頼文と履歴メタデータを生成する。内容だけ確認する場合は `--dry-run` を使う。
3. 生成した依頼文が、対象ログ、ユーザー主観、評価観点、不確実性、Codexへの引き継ぎ要件を含むことを確認する。

## 回答を反映判断する

1. [回答反映テンプレート](../../../data/prompts/apply-garmin-coach-feedback.md) を読み、返却本文を日付付きMarkdownとして `data/logs/reviews/` に保存する。
2. 提案ごとに、確認済み事実・推論・未確認事項を分け、現行メニューとログに照合する。
3. 根拠不足、変更不要、データ不足は有効な結論として保存し、メニュー本体を変えない。採用する具体的な改定だけ `$revise-training-menu` に渡す。

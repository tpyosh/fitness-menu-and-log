# Apply Garmin Coach Feedback Template

このテンプレートは、ChatGPTのGarminコーチングレビュー結果をCodexに貼り戻し、リポジトリ変更へ変換するためのものです。

## Codexへの依頼テンプレート

```md
以下は、ChatGPTによるGarmin Coaching Reviewです。
このリポジトリの `AGENTS.md` を守り、提案を鵜呑みにせず、具体的で根拠のある変更だけを反映してください。

# 1. ChatGPTレビュー本文

{{chatgpt_feedback}}

# 2. Codexにしてほしいこと

- ChatGPTレビューを読み、具体的で実行可能な変更だけを抽出してください
- 曖昧なモチベーション、一般論、データで支えられていない助言は無視してください
- メニュー、設計思想、ログ記録ルール、プロンプト、ドキュメントの更新は、レビュー内容が明確に正当化する場合だけ行ってください
- このリポジトリの元の意図を保ってください
- 変更は小さく、レビューしやすい範囲にしてください
- 何を変更したか、なぜ変更したか、どのレビュー項目が根拠かを説明してください
- レビューが「No change recommended」または実質的に変更不要という結論なら、メニュー本体は変更しないでください
- 変更不要の場合は、必要に応じてレビュー結果だけを `data/logs/reviews/` に保存してください
- レビュー依頼メタデータの `data/logs/reviews/review-request-history.jsonl` には、ChatGPT回答本文を保存しないでください

# 3. 更新時の制約

- メニュー更新時は `README.md` 冒頭、`data/menus/current-menus.md`、`data/menus/menu-history.md` を同時更新してください
- 設計思想が変わる場合だけ `data/menus/design-philosophy.md` も更新してください
- 推測で重量、回数、セット数、レスト、速度、傾斜を補わないでください
- 単発ログで現行メニューと違う重量を使っただけの場合、現行メニュー本体を自動更新しないでください
- 更新後は `README.md` と `data/menus/current-menus.md` の数値、順序、A/B/C区分が一致しているか確認してください
- 軽量チェックがあれば実行してください
```

## Codexの判断ルール

- `No change recommended`
  - メニュー本体は変更しない
  - 必要ならレビュー結果をMarkdownで保存する
- `Minor adjustment recommended`
  - 根拠、対象ファイル、具体値が明確なものだけ反映する
  - 反映しない提案があれば理由を書く
- `Clear menu change recommended`
  - 変更対象を最小限に絞る
  - `menu-history.md` に理由と差分概要を残す
- `Insufficient data`
  - 原則としてメニュー本体は変更しない
  - 次回以降に記録すべき指標や主観メモだけを保存する

## レビュー結果の保存先

ChatGPTの回答本文を保存する場合は、`data/logs/reviews/` 配下に日付つきMarkdownで保存する。

推奨命名:

- `YYYY-MM-DD_garmin-coach-review-response.md`
- 同日に複数ある場合は `YYYY-MM-DD_HHMM_garmin-coach-review-response.md`

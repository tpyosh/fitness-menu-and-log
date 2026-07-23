# Review Storage

このディレクトリには、ChatGPTレビュー結果やメニュー改定提案を保管します。

新規ログごとの通常フィードバックと `keep` / `adjust` / `defer` 判断はここへ別ファイルとして増やさず、対象セッションの `data/logs/structured/sessions.yaml` に保存します。このディレクトリはオンデマンドの外部レビューと改定提案の保管用です。

## 置くもの

- ChatGPTへ送ったレビュー依頼文のコピー
- ChatGPTから返ってきた提案
- 提案を採用するかどうかの判断メモ
- オンデマンドGarminコーチングレビューの依頼メタデータ履歴

## 命名ルールの目安

- `YYYY-MM-DD_review-request.md`
- `YYYY-MM-DD_review-response.md`
- `YYYY-MM-DD_menu-change-note.md`
- `YYYY-MM-DD_garmin-coach-review-request.md`
- `YYYY-MM-DD_garmin-coach-review-response.md`

## レビュー依頼履歴

オンデマンドGarminコーチングレビューの依頼履歴は、本文とは分けて `review-request-history.jsonl` に保存します。

1行1レビュー依頼で、可能な範囲で以下を記録します。

- `requested_at`
- `timestamp_precision`
- `repo_state`
- `previous_review_requested_at`
- `log_range_covered`
- `files_used`
- `prompt_file`
- `short_summary`
- `notes`

ChatGPTの回答本文はこのJSONLには入れません。回答を保存する場合は、日付つきMarkdownとして別ファイルに保存します。

## 依頼文の生成

新しいGarminコーチングレビュー依頼を作る場合は、以下を使います。

```sh
python3 scripts/generate_garmin_coach_review_prompt.py
```

履歴更新なしで確認する場合は以下を使います。

```sh
python3 scripts/generate_garmin_coach_review_prompt.py --dry-run
```

## 注意

- 提案を保存しても、最新メニューの正本は `data/menus/current-menus.md`
- 採用した変更は、必ず `data/menus/menu-history.md` にも残す
- ChatGPTレビューは外部意見であり、具体的な根拠のある変更だけを採用する
- 変更不要というレビュー結果なら、メニュー本体は更新しない

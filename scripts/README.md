# Scripts

このディレクトリは、補助スクリプト置き場です。正本はあくまで `data/` 配下のMarkdown / CSV / YAML / JSONLで、スクリプトは読み取りと下書き生成を補助します。

## 今日のメニューをApple Notesへ出力

`export_today_menu_to_apple_notes.py` は、`data/menus/current-menus.md` から指定したA/B/Cメニューを読み取り、Apple Notesの固定ノート `今日のトレーニングメニュー` へ出力します。

```sh
python3 scripts/export_today_menu_to_apple_notes.py --menu A
```

- `--menu` は `A` / `B` / `C` のいずれかを指定する
- 固定ノートがなければ、Apple Notesのデフォルトアカウント・デフォルトフォルダに新規作成する
- 固定ノートがあれば、本文を今回のスナップショットで完全に置換する
- 同名ノートが複数ある場合は、意図しないノートを更新しないようエラーにする
- 初回はmacOSからNotesのオートメーション操作許可を求められることがある

Apple Notesを変更せず、出力内容だけ確認する場合:

```sh
python3 scripts/export_today_menu_to_apple_notes.py --menu B --dry-run
```

## Garminコーチングレビュー依頼生成

`generate_garmin_coach_review_prompt.py` は、前回レビュー依頼以降のGarminログを抽出し、ChatGPTへ貼るレビュー依頼文を生成するスクリプトです。

通常実行:

```sh
python3 scripts/generate_garmin_coach_review_prompt.py
```

実行すると以下を行います。

- `data/logs/reviews/review-request-history.jsonl` から直近のレビュー依頼を確認する
- `data/logs/structured/sessions.csv` を主に使って対象ログを抽出する
- `sessions.yaml` を読み込める環境では、セグメント詳細やマシン調整もプロンプトに含める
- `data/logs/reviews/YYYY-MM-DD_garmin-coach-review-request.md` に依頼文を保存する
- `data/logs/reviews/review-request-history.jsonl` に今回の依頼メタデータを追記する

履歴やファイルを更新せずに確認する場合:

```sh
python3 scripts/generate_garmin_coach_review_prompt.py --dry-run
```

任意メモを添える場合:

```sh
python3 scripts/generate_garmin_coach_review_prompt.py --notes "今回見てほしい観点"
```

## 今後追加する可能性がある用途

- CSVとYAMLの整合確認
- ログ追加時の雛形生成

追加するときも、このリポジトリの正本はあくまでテキストファイル本体です。スクリプトは補助に留めます。

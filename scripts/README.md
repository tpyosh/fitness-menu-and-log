# Scripts

このディレクトリは、補助スクリプト置き場です。正本はあくまで `data/` 配下のMarkdown / CSV / YAML / JSONで、スクリプトは読み取りと下書き生成を補助します。

## コード構成

トップレベルのPythonスクリプトは引数の受付と処理の呼び出しを担当し、共通処理は `fitness/` に分けています。

| ファイル | 役割 |
| --- | --- |
| `fitness/paths.py` | リポジトリの基準ディレクトリと正本ファイルのパス |
| `fitness/prescriptions.py` | 処方スナップショット・試行の検証、日付に応じた処方の選択 |
| `fitness/execution.py` | 処方・試行・本人申告・直接観測の統合と根拠の保持 |
| `fitness/review_data.py` | 最新レビュー依頼状態、CSV、YAMLの読み取りと出力先の解決 |
| `fitness/review_rendering.py` | 渡されたデータと本文からレビュー依頼文を生成 |

既存の `python3 scripts/<スクリプト名>.py` に加え、リポジトリのルートから `python3 -m scripts.<スクリプト名>` でも実行できます。Pythonから利用する場合は、例えば `from scripts.fitness.execution import resolve_session` として読み込みます。従来のスクリプトからのヘルパー関数のインポートも維持しています。

レビュー依頼文の生成処理はファイルの読み取りから分離しているため、テストでは正本ファイルを編集せずに任意のメニューやログを渡せます。PyYAMLがない場合にYAMLを原文として抜粋する動作も維持しています。

## 今日のメニューをApple Notesへ出力

`export_today_menu_to_apple_notes.py` は、`data/menus/current-menus.md` から指定したA/B/Cメニューを読み取り、Apple Notesの固定ノート `今日のトレーニングメニュー` へ出力します。

```sh
python3 scripts/export_today_menu_to_apple_notes.py --menu A
```

- `--menu` は `A` / `B` / `C` のいずれかを指定する
- Cのモードが決まっている場合は、`--c-mode recovery` / `--c-mode standard` / `--c-mode endurance` を併記すると選択したモードだけを出力する
- 固定ノートがなければ、Apple Notesのデフォルトアカウント・デフォルトフォルダに新規作成する
- 固定ノートがあれば、本文を今回のスナップショットで完全に置換する
- 同名ノートが複数ある場合は、意図しないノートを更新しないようエラーにする
- 初回はmacOSからNotesのオートメーション操作許可を求められることがある

Apple Notesを変更せず、出力内容だけ確認する場合:

```sh
python3 scripts/export_today_menu_to_apple_notes.py --menu B --dry-run
```

CのStandardだけを出力する場合:

```sh
python3 scripts/export_today_menu_to_apple_notes.py --menu C --c-mode standard
```

## Garminコーチングレビュー依頼生成

`generate_garmin_coach_review_prompt.py` は、前回レビュー依頼以降のGarminログを抽出し、ChatGPTへ貼るレビュー依頼文を生成するスクリプトです。

通常実行:

```sh
python3 scripts/generate_garmin_coach_review_prompt.py
```

実行すると以下を行います。

- `data/logs/reviews/review-request-state.json` から直近の依頼日時を確認する
- `data/logs/structured/sessions.csv` を主に使って対象ログを抽出する
- `sessions.yaml` を読み込める環境では、セグメント詳細やマシン調整もプロンプトに含める
- `current-assessment.md`と`backlog.md`の本文を埋め込み、`data/logs/reviews/review-request.md`へ上書きする
- `data/logs/reviews/review-request-state.json`へ最新メタデータを上書きする。日付付き依頼やJSONL履歴は増やさない
- 判断とバックログは生成時に変更しない。返却回答を照合して既存IDを更新する

ファイルを更新せずに確認する場合:

```sh
python3 scripts/generate_garmin_coach_review_prompt.py --dry-run
```

任意メモを添える場合:

```sh
python3 scripts/generate_garmin_coach_review_prompt.py --notes "今回見てほしい観点"
```

## 今後追加する可能性がある用途

- ログ追加時の雛形生成

追加するときも、このリポジトリの正本はあくまでテキストファイル本体です。スクリプトは補助に留めます。

## 処方と実績の解釈

`workout_feedback.py` は日付・A/B/Cから版付き処方と有効な次回限定試行を解決し、メニュー完遂の申告を受けた場合に処方を実施基準へ継承する。`--deviations-json`と`--observations-json`で種目・項目単位の差分を重ねられる。直接観測の矛盾や処方欠損はエラーになる。

```sh
python3 scripts/workout_feedback.py --date 2026-10-06 --menu A --completed
ruby scripts/validate_fitness_data.rb
python3 -m unittest discover -s tests
```

`validate_fitness_data.rb` はCSV/YAMLのセッション対応、処方ID、本文ハッシュ、試行参照、新形式ログの重量整合、レビュー判断・課題の必須項目・ID・相互参照と依頼状態を検証する。

Pythonのテストは、処方と観測の解釈に加え、日付による版の切り替え、YAMLの原文抜粋、直接実行とモジュール実行、リポジトリ外からの実行、レビューの `--dry-run` がファイルを更新しないことを確認する。Apple Notesの実更新は行わない。

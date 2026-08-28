# fitness-menu-and-log

## 最新メニュー Quick Reference（2026-08-11時点）

この冒頭セクションを、ユーザがGitHubアプリですぐ確認するための最新メニューとして運用する。完全版は `data/menus/current-menus.md` を参照し、メニュー変更時は `README.md` 冒頭、`data/menus/current-menus.md`、`data/menus/menu-history.md` を必ず同期する。

### A（Lower emphasis + Upper）

- WU 8分: 6.3 km/h, 傾斜 11%
- Seated Leg Press: 125kg（参考）x 12〜15回 x 3set, RIR 2〜3, rest 90秒
- Seated Leg Curl: 40kg（参考）x 10〜15回 x 2set, RIR 2〜3, rest 60〜75秒
- Leg Extension: 40kg（参考）x 10〜15回 x 2set, RIR 2〜3, rest 60〜75秒
- Lat Pulldown: 40kg（参考）x 8〜12回 x 2set, RIR 2〜3, rest 90秒
- Chest Press: 33kg（参考）x 8〜12回 x 2set, RIR 2〜3, rest 90秒
- Hip Abduction: 61kg（参考）x 12〜15回 x 2set, RIR 2〜3, rest 60秒
- Abdominal: 42.5kg（参考）x 10〜15回 x 2set, RIR 2〜3, rest 60秒
- トレッドミル 18分: 6.2 km/h・12% x 6分 → 6.3 km/h・13% x 6分 → 6.2 km/h・14% x 6分

### B（Upper emphasis + Lower）

- WU 8分: 6.3 km/h, 傾斜 11%
- Lat Pulldown: 40kg（参考）x 8〜12回 x 3set, RIR 2, rest 90秒
- Row Machine: 40kg（参考）x 8〜12回 x 3set, RIR 2, rest 90秒
- Chest Press: 33kg（参考）x 8〜12回 x 3set, RIR 2, rest 90秒
- Shoulder Press: 20kg（参考）x 8〜12回 x 2set, RIR 2〜3, rest 90秒
- Seated Leg Press: 115kg（参考）x 12〜15回 x 2set, RIR 3, rest 90秒
- Seated Leg Curl: 40kg（参考）x 10〜15回 x 2set, RIR 2〜3, rest 60〜75秒
- Torso Rotation: 57.5kg（参考）左右10〜12回 x 1set, RIR 3, rest 60秒
- Abdominal: 42.5kg（参考）x 10〜15回 x 2set, RIR 2〜3, rest 60秒
- トレッドミル 16分: 6.2 km/h・11% x 6分 → 6.3 km/h・11% x 6分 → 6.2 km/h・12% x 4分

詳細なフォーム指示、評価軸、補足意図は `data/menus/current-menus.md` を参照する。

全種目はDouble Progressionで運用する。詳細を記録できる場合はreps・RIR・フォームで進行を判定する。通常ログでは負荷感、筋肉痛、運動中の痛み・明確なフォーム問題を最小主観入力とし、反復する「軽い」という所感に重大な反証がなければ、正本を変える前に次回だけ1段上を試せる。Optional Cは20〜40分のeasy cardio中心で、行かなくてもA/Bだけで完結する。

このリポジトリは、フィットネスメニューとGarminログをローカルなテキスト資産として管理するための正本です。目的は、最新メニュー、過去ログ、レビュー履歴をMarkdown / YAML / CSVで堅実に維持し、新しいログを記録するたびにフィードバックとメニュー判断まで完結させることです。ChatGPTへのオンデマンドレビューは、複数ログを外部視点で再検討したい場合の補助運用です。

## このリポジトリの役割

- `README.md` 冒頭で、ユーザ向けの最新A/BメニューQuick Referenceを確認できるようにする
- `data/menus/current-menus.md` で、LLM参照用の完全なA/Bメニューを管理する
- Garminログ画像から転記した内容を、検索しやすいテキストとして蓄積する
- 新しいログごとに、同種の直近履歴との比較、日本語フィードバック、`keep` / `adjust` / `defer` のメニュー判断を残す
- ChatGPTへ送るレビュー依頼プロンプトのテンプレートを保持する
- ChatGPTから返ってきた提案を、そのまま鵜呑みにせずレビュー履歴として保存する

## 最初に見るファイル

- `README.md`
  - GitHubアプリですぐ見るための最新メニューQuick Reference
- `data/menus/current-menus.md`
  - 現在の最新A60 / B60の完全版
- `data/menus/design-philosophy.md`
  - なぜそのメニュー構成なのか
- `data/logs/structured/README.md`
  - Garmin画像から何をどう転記するか
- `AGENTS.md`
  - Codexが更新時に守るべきルール

## 日常運用フロー

1. ユーザがGarminログ画像を取得する
2. 必要に応じて画像ファイルを `data/logs/raw/` 配下のルールに沿って置く、または参照元を明記する
3. Codexが `data/prompts/log-intake-template.md` を使って画像内容をテキスト化する
4. ユーザが短い主観として、負荷感、筋肉痛の有無・部位・程度、運動中の痛みまたは明確なフォーム問題を伝える。判断に必要な情報が欠ける場合はCodexが1〜3問だけ確認する
5. Codexが `data/logs/structured/sessions.csv` と `data/logs/structured/sessions.yaml` を同時更新する
6. Codexが直近8週間の同種セッションを新しい順に最大3件確認し、事実、解釈、仮説を分けて日本語フィードバックを作る
7. Codexが正本の `keep` / `adjust` / `defer` と、次回行動の `maintain` / `trial_one_step` / `reduce` / `stop` を分けて判断し、YAMLへ保存する
8. `adjust` は原則として少なくとも2回の比較可能な完遂セッションで同方向の根拠が続き、重大な反証がない場合だけ採用する。採用時は `README.md` 冒頭、`data/menus/current-menus.md`、`data/menus/menu-history.md` を同時更新する
9. 設計思想そのものが変わる場合のみ、`data/menus/design-philosophy.md` も更新する

判断に必要な情報が欠ける場合は `pending_user_input` として質問し、未質問の欠損を理由に `defer` へ送らない。通常の単発好成績、1回だけの重量変更、Garminスコアだけを根拠に恒久メニューを変更しないが、正本を維持した次回試行とは区別する。明示的な痛みや異常症状など安全上の懸念は、単発でも中止、保留、負荷低減の理由にできる。

## オンデマンドGarminコーチングレビュー

通常取り込みで行う内蔵フィードバックとは別に、前回レビュー依頼以降のGarminログをまとめてChatGPTに見せたい場合は、以下を使う。

```sh
python3 scripts/generate_garmin_coach_review_prompt.py
```

このコマンドは以下を行う。

- `data/logs/reviews/review-request-history.jsonl` から前回レビュー依頼日時を確認する
- `data/logs/structured/sessions.csv` と `data/logs/structured/sessions.yaml` から、前回依頼以降のログを抽出する
- 件数が少ない場合に備えて、直前の数セッションを比較用ベースラインとして添える
- ChatGPTへ貼る依頼文を `data/logs/reviews/YYYY-MM-DD_garmin-coach-review-request.md` に保存する
- 今回のレビュー依頼メタデータを `data/logs/reviews/review-request-history.jsonl` に追記する

履歴を更新せずに内容だけ確認する場合は、以下を使う。

```sh
python3 scripts/generate_garmin_coach_review_prompt.py --dry-run
```

生成されたMarkdown本文をChatGPTに貼り付ける。ChatGPTの回答をCodexに貼り戻して反映したい場合は、`data/prompts/apply-garmin-coach-feedback.md` のテンプレートに沿って依頼する。Codexは、具体的で根拠のある変更だけを抽出し、変更不要という結論ならメニュー本体を更新しない。

## 正本ファイル

- ユーザ向け最新メニューQuick Reference: `README.md` 冒頭
- 最新メニュー完全版の正本: `data/menus/current-menus.md`
- 設計思想の正本: `data/menus/design-philosophy.md`
- メニュー変更履歴の正本: `data/menus/menu-history.md`
- ジムにあるマシン一覧の正本: `data/machines/gym-machines.yaml`
- セッション要約一覧の正本: `data/logs/structured/sessions.csv`
- セッション詳細ログの正本: `data/logs/structured/sessions.yaml`
- ChatGPTレビュー用テンプレートの正本: `data/prompts/chatgpt-review-template.md`
- オンデマンドGarminレビュー依頼テンプレート: `data/prompts/garmin-coach-review-request.md`
- ChatGPTレビュー反映テンプレート: `data/prompts/apply-garmin-coach-feedback.md`
- レビュー依頼メタデータ履歴: `data/logs/reviews/review-request-history.jsonl`

## ディレクトリ概要

- `data/machines/`
  - ジムにある設備・マシンの正本
- `data/menus/`
  - 最新メニュー、設計思想、変更履歴
- `data/logs/raw/`
  - Garminスクリーンショットなどの元資料置き場
- `data/logs/structured/`
  - Garminログの転記結果
- `data/logs/reviews/`
  - ChatGPTのレビュー依頼、レビュー結果、改定提案、レビュー依頼メタデータの保管場所
- `data/prompts/`
  - Codexが使うテンプレート
- `scripts/`
  - 将来の補助スクリプト置き場

## 運用の前提

- このリポジトリは、まず人間が読めることを優先する
- 推測で重量、回数、意図を補わない
- マシンは筋刺激、トレッドミルは心肺、という現行思想を基準に扱う
- Garminの数値は重要だが、A日とB日で評価の重みづけを変える
- マシンのみで終えた日は、正規A/Bとは別カテゴリとして記録する

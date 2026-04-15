# fitness-menu-and-log

## 最新メニュー Quick Reference（2026-04-11時点）

この冒頭セクションを、ユーザがGitHubアプリですぐ確認するための最新メニューとして運用する。完全版は `data/menus/current-menus.md` を参照し、メニュー変更時は `README.md` 冒頭、`data/menus/current-menus.md`、`data/menus/menu-history.md` を必ず同期する。

### A60

- WU 8分: 6.3 km/h, 傾斜 11%
- Seated Leg Press: 115kg x 15回 x 4set, rest 45〜60秒
- Leg Extension: 40kg x 12回 x 3set, rest 30秒
- Seated Leg Curl: 40kg x 12回 x 3set, rest 30秒
- Hip Abduction: 61kg x 15回 x 2set, rest 30秒
- Hip Adduction: 61kg x 12回 x 最大2set, 張りが強ければ1setで終了, rest 30秒
- Abdominal: 42.5kg x 12回 x 3set, rest 30秒
- トレッドミル 18分: 6.2 km/h・12% x 6分 → 6.3 km/h・13% x 6分 → 6.2 km/h・14% x 6分

### B60

- WU 8分: 6.3 km/h, 傾斜 11%
- Lat Pulldown: 40kg x 12回 x 4set, rest 45秒
- Row Machine: 40kg x 12回 x 4set, rest 45秒
- Chest Press: 26kg x 12回 x 3set, rest 45秒
- Shoulder Press: 15kg x 10回 x 3set, rest 45秒
- Torso Rotation: 50kg 左右12回 x 2set, rest 30秒
- Abdominal: 42.5kg x 12回 x 3set, rest 30秒
- トレッドミル 16分: 6.2 km/h・11% x 6分 → 6.3 km/h・11% x 6分 → 6.2 km/h・12% x 4分

詳細なフォーム指示、評価軸、補足意図は `data/menus/current-menus.md` を参照する。

このリポジトリは、フィットネスメニューとGarminログをローカルなテキスト資産として管理するための正本です。目的は、最新メニュー、過去ログ、レビュー履歴をMarkdown / YAML / CSVで堅実に維持し、必要なときだけChatGPTへレビュー依頼できる運用基盤を作ることです。

## このリポジトリの役割

- `README.md` 冒頭で、ユーザ向けの最新A/BメニューQuick Referenceを確認できるようにする
- `data/menus/current-menus.md` で、LLM参照用の完全なA/Bメニューを管理する
- Garminログ画像から転記した内容を、検索しやすいテキストとして蓄積する
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
4. Codexが `data/logs/structured/sessions.csv` と `data/logs/structured/sessions.yaml` を同時更新する
5. メニュー見直しが必要なときだけ、`data/prompts/chatgpt-review-template.md` をもとにChatGPTへ送るレビュー依頼文を作る
6. ChatGPTの回答を採用する場合は、`README.md` 冒頭、`data/menus/current-menus.md`、`data/menus/menu-history.md` を同時更新する
7. 設計思想そのものが変わる場合のみ、`data/menus/design-philosophy.md` も更新する

## 正本ファイル

- ユーザ向け最新メニューQuick Reference: `README.md` 冒頭
- 最新メニュー完全版の正本: `data/menus/current-menus.md`
- 設計思想の正本: `data/menus/design-philosophy.md`
- メニュー変更履歴の正本: `data/menus/menu-history.md`
- ジムにあるマシン一覧の正本: `data/machines/gym-machines.yaml`
- セッション要約一覧の正本: `data/logs/structured/sessions.csv`
- セッション詳細ログの正本: `data/logs/structured/sessions.yaml`
- ChatGPTレビュー用テンプレートの正本: `data/prompts/chatgpt-review-template.md`

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
  - ChatGPTのレビュー結果や改定提案の保管場所
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

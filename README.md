# fitness-menu-and-log

このリポジトリは、フィットネスメニューとGarminログをローカルなテキスト資産として管理するための正本です。目的は、最新メニュー、過去ログ、レビュー履歴をMarkdown / YAML / CSVで堅実に維持し、必要なときだけChatGPTへレビュー依頼できる運用基盤を作ることです。

## このリポジトリの役割

- 最新のA/Bメニューを正本として管理する
- Garminログ画像から転記した内容を、検索しやすいテキストとして蓄積する
- ChatGPTへ送るレビュー依頼プロンプトのテンプレートを保持する
- ChatGPTから返ってきた提案を、そのまま鵜呑みにせずレビュー履歴として保存する

## 最初に見るファイル

- `data/menus/current-menus.md`
  - 現在の最新A60 / B60
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
6. ChatGPTの回答を採用する場合は、`data/menus/current-menus.md` と `data/menus/menu-history.md` を同時更新する
7. 設計思想そのものが変わる場合のみ、`data/menus/design-philosophy.md` も更新する

## 正本ファイル

- 最新メニューの正本: `data/menus/current-menus.md`
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

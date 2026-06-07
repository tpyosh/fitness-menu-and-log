# AGENTS.md

このファイルは、このリポジトリを扱うCodex向けの運用ルールです。目的は、最新メニュー、Garminログ、レビュー履歴を壊さずに更新することです。

## 基本方針

- ユーザが最新メニューを最初に確認する場所は、レポジトリ直下の `README.md` 冒頭とする
- `README.md` 冒頭はユーザ向けQuick Reference、`data/menus/current-menus.md` はLLM参照用の完全なメニューとして扱う
- このリポジトリはフィットネスメニュー管理のソースオブトゥルースとして扱う
- 画像解析そのものを勝手に進めず、ユーザが渡したGarmin情報を正確にテキスト化して残す
- ChatGPTは外部レビュアーであり、提案をそのまま正解扱いしない
- 推測で重量、回数、セット数、傾斜、速度、意図を改変しない
- `data/machines/weight-options/*.md` は、ジムマシンの重量スタック表示の正本として扱う
- ユーザが「1段重い」「1段軽い」「次の重量」などの相対表現を使った場合、対象マシンの現行メニュー重量と `data/machines/weight-options/*.md` から一意に解決できる重量は、推測ではなく参照確定値として扱う

## 更新ルール

- メニュー更新時は `README.md` 冒頭、`data/menus/current-menus.md`、`data/menus/menu-history.md` を同時更新する
- 設計思想が変わった場合は `data/menus/design-philosophy.md` も更新する
- Garminログを追加したら `data/logs/structured/sessions.csv` と `data/logs/structured/sessions.yaml` の両方を更新する
- ユーザが「ChatGPTに送る用のプロンプトを書いて」と言ったら、`data/prompts/chatgpt-review-template.md` を元に今回用のレビュー依頼文を生成する
- ユーザがChatGPTからの修正案を貼ったら、内容を鵜呑みにせず、どのファイルをどう更新するかを明示してから更新する
- レビュー結果や提案文を保存する場合は `data/logs/reviews/` 配下に日付つきMarkdownで残す
- `README.md` 冒頭のQuick Referenceは `data/menus/current-menus.md` の数値と順序を要約したものとして維持し、推測で補わない
- メニュー更新後は `README.md` と `data/menus/current-menus.md` の重量、回数、セット数、レスト、速度、傾斜、順序が一致しているか確認する
- ログ入力で相対的な重量変更が出た場合は、`data/menus/current-menus.md` と対象マシンの `data/machines/weight-options/*.md` を確認してから、CSV/YAMLに具体重量を記録する

## 勝手に変えてはいけないもの

- ユーザが明示していないメニュー変更
- 与えられていない重量、回数、セット数、レスト秒数の補完
- A/Bの役割分担の勝手な再解釈
- Garminログの分類ルールの改変
- `data/machines/gym-machines.yaml` にあるマシン一覧の無断編集
- 単発ログで現行メニューと違う重量を使っただけの場合の、現行メニュー本体の自動更新

## ログ記録ルール

- `session_type` は `A_full` / `B_full` / `A_machine_only` / `B_machine_only` / `treadmill_only` / `extra_treadmill` を使う
- `segment_type` は少なくとも `warmup` / `machine` / `treadmill_main` / `cooldown` / `extra_treadmill` を使える形で保持する
- ユーザから明示的に指定がない限り、A60 / B60 のラップ解釈は `Lap 1 = warmup`、`Lap 2 = machine`、`Lap 3 = treadmill_main`、`Lap 4 = cooldown` とする
- 上記の日本語対応は、1ラップ目 = トレッドミルアップ、2ラップ目 = マシン、3ラップ目 = トレッドミル心肺刺激、4ラップ目 = トレッドミルダウンとする
- CSVは1行1セッションの要約、YAMLは1セッションごとの詳細とセグメント情報を保持する
- マシンのみで終えた日は、フルメニュー達成として扱わない
- ログに不明値がある場合は空欄または `unknown` とし、推測値を入れない
- 「1段重い」「1段軽い」「前回より1段」「ピンを1つ上/下」などの相対重量表現がある場合は、まず `data/menus/current-menus.md` の該当メニュー重量を基準値として確認し、次に対象マシンの `data/machines/weight-options/*.md` で隣接する重量を特定する
- 相対重量表現を具体重量に解決できた場合は、CSVの `menu_deviation` / `notes` と、YAMLの `menu_deviation` / `subjective_notes` / `machine_adjustments` に、基準重量、実施重量、体感、解決根拠を残す
- 対象マシン、基準重量、重量スタック表のいずれかが曖昧で一意に解決できない場合だけ、`unknown` または元の相対表現のまま残し、未解決理由を `notes` に書く

## レビュー運用

- ChatGPTレビュー依頼時は、現行メニュー、設計思想、対象ログ、ユーザ主観、評価してほしい点を揃える
- 依頼文には「必要であればメニューを修正してください」を含める
- ChatGPTの提案を採用した場合は、変更理由と差分概要を `data/menus/menu-history.md` に残す
- ChatGPTの提案を採用してメニューを変えた場合は、`README.md` 冒頭のQuick Referenceも同じ更新で同期する

## 出力の優先順位

1. 正確性
2. 履歴の一貫性
3. 人間が読んで追えること
4. 将来の自動化のしやすさ

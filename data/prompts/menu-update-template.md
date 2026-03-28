# Menu Update Template

ChatGPTの修正案やユーザの指示を受けてメニュー更新するときの、更新漏れ防止用の運用プロンプト兼手順テンプレートです。

## そのまま使える運用プロンプト

```md
メニュー更新を行ってください。以下のルールに従ってください。

- まず、今回更新するファイルと変更理由を明示する
- `README.md` 冒頭の最新メニューQuick Referenceを更新する
- `data/menus/current-menus.md` を完全版として更新する
- `data/menus/menu-history.md` に変更理由と差分概要を追記する
- 設計思想が変わる場合だけ `data/menus/design-philosophy.md` も更新する
- `README.md` には、ジムで見やすい要約だけを書く
- 重量、回数、セット数、レスト、速度、傾斜、種目順は推測で補わず、`data/menus/current-menus.md` と一致させる
- 更新後に `README.md` と `data/menus/current-menus.md` の数値、順序、A/B区分が一致しているか確認する
- 最後に、更新したファイルと変更内容を要約して報告する
```

## Quick Reference運用ルール

- `README.md` 冒頭は、ユーザがGitHubアプリですぐ見るための最新メニューQuick Referenceとする
- `data/menus/current-menus.md` は、LLMが参照する完全なメニューとする
- `README.md` には、種目順、重量、回数、セット数、レスト、トレッドミル条件などの要点を載せる
- 詳細なフォーム指示、評価軸、補足意図は `data/menus/current-menus.md` に残す
- `README.md` の要約は `data/menus/current-menus.md` から転記し、独自解釈を加えない

## 更新前チェック

1. 変更の根拠を確認する
2. 何を更新するかを先に明示する
3. 推測で重量、回数、セット数、傾斜、速度を補わない

## 変更内容整理テンプレート

```md
# 今回の変更対象

- 変更理由:
  {{change_reason}}

- 更新するファイル:
  - README.md
  - data/menus/current-menus.md
  - data/menus/menu-history.md
  - data/menus/design-philosophy.md （設計思想が変わる場合のみ）

# 変更案の確認

- 変更前:
  {{before_summary}}

- 変更後:
  {{after_summary}}

- この変更が必要な理由:
  {{why_this_change}}
```

## 実更新ルール

- `README.md` 冒頭のQuick Referenceを最新状態に更新する
- `data/menus/current-menus.md` を最新状態に更新する
- `data/menus/menu-history.md` に変更日、理由、差分概要を残す
- 設計思想に影響するなら `data/menus/design-philosophy.md` も更新する
- ChatGPTレビュー文そのものを残す場合は `data/logs/reviews/` に保存する

## 更新後チェック

- `README.md` 冒頭と `current-menus.md` の数値、順序、A/B区分が一致しているか
- `current-menus.md` と `menu-history.md` の内容が一致しているか
- 設計思想とメニューの整合性が取れているか
- A/Bの評価軸が更新内容と矛盾していないか

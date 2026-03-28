# Menu Update Template

ChatGPTの修正案やユーザの指示を受けてメニュー更新するときの手順テンプレートです。

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

- `data/menus/current-menus.md` を最新状態に更新する
- `data/menus/menu-history.md` に変更日、理由、差分概要を残す
- 設計思想に影響するなら `data/menus/design-philosophy.md` も更新する
- ChatGPTレビュー文そのものを残す場合は `data/logs/reviews/` に保存する

## 更新後チェック

- `current-menus.md` と `menu-history.md` の内容が一致しているか
- 設計思想とメニューの整合性が取れているか
- A/Bの評価軸が更新内容と矛盾していないか

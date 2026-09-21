---
name: revise-training-menu
description: 確定したログ判断、明示的なユーザー指示、または根拠付きレビューに基づき、A/B/Cの現行メニューを版管理して更新するときに使う。単なるログ記録、次回だけの試行、根拠不足の提案には使わない。
---

# メニュー改定

メニューの正本と履歴を同期し、必要最小限の変更だけを記録する。

1. [現行メニュー](../../../data/menus/current-menus.md)、[設計思想](../../../data/menus/design-philosophy.md)、[改定履歴](../../../data/menus/menu-history.md)、[更新テンプレート](../../../data/prompts/menu-update-template.md) を読む。重量変更では該当する重量表も確認する。
2. 改定前に、根拠、変更する値、変更しない値、対象ファイルを明示する。通常は重量、回数、セット数、レスト、速度、傾斜、時間の主な1次元だけを変える。
3. `README.md` 冒頭のQuick Reference、`current-menus.md`、`menu-history.md` を同じ変更で更新する。設計思想が変わる場合だけ `design-philosophy.md` も更新する。
4. 履歴にはprevious/new version、正確なbefore/after、日付付き根拠、意図する効果、再評価条件、rollbackまたは再検討条件を残す。
5. 更新後、A/B/C区分、順序、重量、回数、セット数、レスト、速度、傾斜がQuick Referenceと完全版で一致することを確認する。

外部レビューは根拠の一つであり、それ自体で採用しない。単発の通常ログ、Garmin単独の良否、次回だけの増量試行では正本を改定しない。

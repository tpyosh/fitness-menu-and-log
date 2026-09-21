# AGENTS.md

このリポジトリは、最新のトレーニングメニュー、Garminログ、レビュー履歴の正本です。正確性、履歴の一貫性、人間が追えることを優先します。

## 正本

- `README.md` 冒頭: ユーザ向け最新メニューQuick Reference
- `data/menus/current-menus.md`: 最新メニュー完全版
- `data/menus/menu-history.md`: メニュー改定履歴
- `data/menus/design-philosophy.md`: 設計思想
- `data/logs/structured/sessions.csv` / `sessions.yaml`: セッションの要約 / 詳細
- `data/machines/gym-machines.yaml` と `data/machines/weight-options/`: マシン識別と重量スタック
- `data/prompts/`、`data/logs/reviews/`、`scripts/`: 既存の手順・レビュー履歴・補助自動化

## 常時守る規約

- ユーザ入力、Garmin表示、推論を区別し、与えられていない重量・回数・セット数・速度・傾斜・症状・意図を補完しない。
- 過去ログは実際の転記誤りを直す場合以外は変更しない。新規ログはCSVとYAMLを同時に更新する。
- メニュー正本を変更する場合は `README.md` 冒頭、`data/menus/current-menus.md`、`data/menus/menu-history.md` を同期する。設計思想が変わる場合だけ `design-philosophy.md` も更新する。
- 単発の通常セッション、Garmin単独の数値、または根拠のない外部提案で恒久メニューを変更しない。
- 相対重量は、現行メニューと該当する重量表から一意に解決できるときだけ具体値として保存する。
- ヒップ系は方向を必ず保持する。構造化IDは `hip_adduction_inward` / `hip_abduction_outward` を使い、方向不明は `hip_abduction_direction_unknown` として原文を残す。
- 胸痛、失神、強い息苦しさ、急な神経症状、持続・悪化する明確な痛みがある場合は、運動の中止と必要に応じた医療専門家への相談を優先する。診断はしない。

## ルーティング

- Garminログの転記・保存・比較・次回判断: `$record-garmin-session`
- 現行メニューの恒久改定と同期: `$revise-training-menu`
- ChatGPTへのGarminコーチングレビュー依頼または回答反映: `$review-garmin-coaching`
- 履歴に基づく読み取り専用のコーチング判断: `fitness-coach` エージェント
- 「今日のメニューをAppleのNoteに出力して」では、A/B/Cが確定していれば `scripts/export_today_menu_to_apple_notes.py --menu <A|B|C>` を実行する。Cのモードも確定している場合は `--c-mode` を付け、未確定なら必要な1問だけ確認する。

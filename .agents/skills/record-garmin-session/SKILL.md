---
name: record-garmin-session
description: Garminログやユーザーのトレーニング実績を正確に保存し、同種の直近履歴との比較、フィードバック、次回判断まで完結するときに使う。現行メニューの恒久改定や外部レビューだけには使わない。
---

# Garminセッション記録

Garmin表示とユーザー発言を観察事実として保存し、記録の完了をフィードバックとメニュー判断までとする。

1. まず [構造化ログの仕様](../../../data/logs/structured/README.md) と [取り込みテンプレート](../../../data/prompts/log-intake-template.md) を読む。対象日の処方を `scripts/workout_feedback.py` / `data/menus/prescriptions.json` から解決し、`current-menus.md` と有効な `active-trials.json` の試行も確認する。必要なマシンの重量表も確認する。
2. 「A60/B60/Cの該当モードを実施」と分かる場合は、処方を実施基準とし、ユーザの変更申告と観測値を項目単位で重ねる。差分なしは直接観測した証拠ではなく `prescribed_no_deviation_reported` として区別する。ユーザが参考重量どおりと確認した場合は直接申告として記録する。回数範囲を正確な実施回数へ変換しない。不明値を推測せず、`sessions.csv` の1行要約と `sessions.yaml` の詳細を同じセッションとして追加する。相対重量は、基準メニューと重量表から一意に決まる場合だけ具体値にする。
3. 直近8週間の同種セッションを新しい順に最大3件比較する。A/Bは同種、Cは同じ `c_mode`、マシンは同じIDだけを比較対象にする。
4. YAMLに、観察事実と分けた日本語の `feedback` と `menu_decision` を残す。判断に必要な最小主観が欠ける場合も事実は保存し、1〜3問だけ確認して `pending_user_input` を使う。
5. [現在のレビュー判断](../../../data/logs/reviews/current-assessment.md)と[バックログ](../../../data/logs/reviews/backlog.md)に関係するログなら、既存J/B-IDの根拠・次の確認・解決状態も同期する。解決条件を満たさない課題は閉じず、日付付きレビューメモは作らない。
6. 返答では、今回の完遂内容、比較結果、次回の具体策、判断の根拠と限界を日本語で簡潔に示す。

恒久的な `adjust` が確定したときだけ `$revise-training-menu` を読み、正本改定と履歴記録を行う。単発の重量変更や試行は、正本を変更せず `keep` と次回行動を記録する。

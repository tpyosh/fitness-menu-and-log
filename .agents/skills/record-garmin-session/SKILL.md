---
name: record-garmin-session
description: Garminログやユーザーのトレーニング実績を正確に保存し、同種の直近履歴との比較、フィードバック、次回判断まで完結するときに使う。現行メニューの恒久改定や外部レビューだけには使わない。
---

# Garminセッション記録

Garmin表示とユーザー発言を観察事実として保存し、記録の完了をフィードバックとメニュー判断までとする。

1. まず [構造化ログの仕様](../../../data/logs/structured/README.md) と [取り込みテンプレート](../../../data/prompts/log-intake-template.md) を読む。Garmin Connectから未取得なら [取得Skill](../fetch-garmin-connect-session/SKILL.md)を使う。取得済みの結果は再取得せず受け取り、取得のみの依頼なら保存しない。追加前に既存ログを照合し、同一activityや既存セッションを二重登録しない。対象日の処方を `scripts/workout_feedback.py` / `data/menus/prescriptions.json` から解決し、`current-menus.md` と有効な `active-trials.json` の試行も確認する。必要なマシンの重量表も確認する。
2. 「A60/B60/Cの該当モードを実施」と分かる場合は、処方を実施基準とし、ユーザの変更申告と観測値を項目単位で重ねる。差分なしは直接観測した証拠ではなく `prescribed_no_deviation_reported` として区別する。ユーザが参考重量どおりと確認した場合は直接申告として記録する。回数範囲を正確な実施回数へ変換しない。不明値を推測せず、`sessions.csv` の1行要約と `sessions.yaml` の詳細を同じセッションとして追加する。相対重量は、基準メニューと重量表から一意に決まる場合だけ具体値にする。
3. 直近8週間の同種セッションを新しい順に最大3件比較する。A/Bは同種、Cは同じ `c_mode`、マシンは同じIDだけを比較対象にする。
4. YAMLに、観察事実と分けた日本語の `feedback` と `menu_decision` を残す。主要値・ラップ・ゾーン・主観の小さな欠損でも保存を進め、痛み・RPE・筋肉痛・回数を毎回一律に質問しない。未申告を「痛みなし」にしない。安全や次回判断が実質的に変わる情報だけ、既存文脈で補えなければ1〜3問に絞り、判断を `pending_user_input` とする。それ以外は限界と再評価条件を添えて判断する。
5. [現在のレビュー判断](../../../data/logs/reviews/current-assessment.md)と[バックログ](../../../data/logs/reviews/backlog.md)に関係するログなら、既存J/B-IDの根拠・次の確認・解決状態も同期する。解決条件を満たさない課題は閉じず、日付付きレビューメモは作らない。
6. 保存後は `ruby scripts/validate_fitness_data.rb` を実行する。返答は何を記録できたかと次回への短い一言を中心にし、比較・欠損・判断の限界は必要な範囲だけ添える。

恒久的な `adjust` が確定したときだけ `$revise-training-menu` を読み、正本改定と履歴記録を行う。単発の重量変更や試行は、正本を変更せず `keep` と次回行動を記録する。

# Structured Garmin Logs

このディレクトリでは、Garmin画像から転記した内容を構造化して保持します。

## 使い分け

- `sessions.csv`
  - 1行1セッションの一覧表
  - 日付、分類、主要Garmin指標、メモを素早く見返すために使う
- `sessions.yaml`
  - 1セッションごとの詳細記録
  - ラップ情報、主観メモ、メニュー逸脱、補足説明に加え、取り込み後のフィードバックとメニュー判断を残すために使う

## Garmin画像から最低限転記する項目

- 共通
  - `date`
  - `session_type`
  - `segment_type`
  - `duration_min`
  - `avg_hr`
  - `max_hr`
  - `aerobic_te`
  - `anaerobic_te`
  - `exercise_load`
  - `calories`
  - `primary_benefit`
  - `notes`
- 任意
  - `avg_temp`
  - `zone1_time`
  - `zone2_time`
  - `zone3_time`
  - `zone4_time`
  - `zone5_time`
  - `subjective_fatigue`
  - `soreness_next_day`
  - `machine_order_changed`
  - `menu_deviation`
  - `machine_adjustments`

## 取り込み後に必須の項目

Garminからの転記事実とは別に、新規ログごとに以下を `sessions.yaml` へ保存する。

- `feedback`
- `menu_decision`

## ユーザの最小入力

詳細なreps・RIRは任意とし、通常は次の短い主観だけを確認する。

- 全体または種目別の負荷感: `軽い` / `適正` / `重い` / `混在`
- 筋肉痛: `なし` / `軽い` / `強い` と部位
- 運動中の痛みまたは明確なフォーム問題: `なし` / `あり` と内容

判断に必要な項目が欠けている場合、CodexはGarmin事実の保存を進めつつ、判断確定前に1〜3問だけユーザへ確認する。未質問の欠損を理由に `defer` としない。

## セッション分類ルール

- `A_full`
  - Aマシン + トレッドミルを実施した正規A日
- `B_full`
  - Bマシン + トレッドミルを実施した正規B日
- `A_machine_only`
  - Aのマシンのみで終了した短縮版
- `B_machine_only`
  - Bのマシンのみで終了した短縮版
- `treadmill_only`
  - トレッドミルだけの日
- `extra_treadmill`
  - A/Bの後に追加したカロリー消費トレッドミル

## セグメント分類ルール

1セッション内にラップや区切りがある場合は、可能な範囲で以下の `segment_type` を使う。

- `warmup`
- `machine`
- `treadmill_main`
- `cooldown`
- `extra_treadmill`

## ラップ運用ルール

手動ラップを使う場合は、ラップ境界を曖昧にしない。

ユーザから明示的に指定がない限り、A60 / B60 のラップは以下の対応を既定とする。

- `Lap 1`
  - トレッドミルアップ
  - `segment_type = warmup`
- `Lap 2`
  - マシン
  - `segment_type = machine`
- `Lap 3`
  - トレッドミル心肺刺激
  - `segment_type = treadmill_main`
- `Lap 4`
  - トレッドミルダウン
  - `segment_type = cooldown`

- `Lap 1`
  - warmup 開始時に開始する
- `Lap 2`
  - 最初のマシン開始時に切る
- `Lap 3`
  - トレッドミル本体開始時に切る
- `Lap 4`
  - cooldown に入るときは、負荷を下げる前ではなく、負荷を下げた瞬間に切る

特に B日では、`treadmill_main` と `cooldown` の境界が曖昧だと、ログ解釈がぶれやすい。

## B日で追加したい主観メモ

B日は Garmin だけでは主評価を確定しにくいので、可能なら以下を残す。

- 各マシン
  - 最終セット余力: `0` / `1` / `2` / `3+`
  - フォーム: `安定` / `やや崩れ` / `崩れ`
  - 狙い部位感: `入った` / `普通` / `入りにくい`
- セッション直後
  - 背中の張り: `0-2`
  - 胸の張り: `0-2`
  - 肩の張り: `0-2`
  - 腹の張り: `0-2`
  - トレッドミルのきつさ: `楽` / `適正` / `きつい`
- 翌日〜翌々日
  - 軽い筋肉痛の部位
  - だるさ: `なし` / `軽い` / `強い`

## 相対重量表現の扱い

ユーザが「1段重い」「1段軽い」「次の重量」「ピンを1つ上/下」などの相対表現で実施重量を伝えた場合は、推測で `unknown` にしない。

1. `data/menus/current-menus.md` で、その日の現行メニュー上の対象マシン重量を確認する
2. 対象マシンの `data/machines/weight-options/*.md` で、重量スタック上の隣接値を確認する
3. 一意に決まる場合は、CSV/YAMLに具体重量として記録する
4. YAMLでは可能な限り `machine_adjustments` に構造化して残す
5. 単発ログで現行メニューより重い/軽い重量を使っただけでは、現行メニュー本体は更新しない

例:

```yaml
machine_adjustments:
  - machine: chest_press
    planned_weight_kg: 26
    actual_weight_kg: 33
    adjustment: one_step_heavier
    resolution_basis: セッション時点のcurrent-menus.mdにあるB60 Chest Press 26kgと、chest-press.mdの次段33から確定。
    subjective_comment: 体感としては十分。
```

## ヒップマシンの識別ルール

ジム内では内向き・外向きの両方が `Hip Abduction` と案内されるため、表示名だけを識別子にしない。

| 動作 | 構造化ID | メニュー表示名 | 重量表 |
| --- | --- | --- | --- |
| 内向き（股関節内転） | `hip_adduction_inward` | `Hip Adduction (Inward / 内向き)` | `hip-abduction-inward.md` |
| 外向き（股関節外転） | `hip_abduction_outward` | `Hip Abduction (Outward / 外向き)` | `hip-abduction-outward.md` |

- YAMLの `exercise_feedback`、`machine_adjustments.machine`、比較対象の識別には構造化IDを使う
- メニューや人向け文章では方向つき表示名を使い、裸の `Hip Abduction` を新規作成しない
- 方向が確認できない過去・新規データは推測で内向き/外向きへ寄せず、`hip_abduction_direction_unknown` として元表現を残す

## 転記の考え方

- フル版
  - Garmin全体サマリーがあり、主要指標とセグメント内訳も転記できる状態
- マシンのみ版
  - A/Bマシンで終了した日。`session_type` は `A_machine_only` または `B_machine_only`
- トレッドミルのみ版
  - `session_type` は `treadmill_only`
- 追加トレッドミル版
  - A/B後に別枠で実施した場合は `extra_treadmill` として記録する

## 更新時の注意

- CSVとYAMLは同じセッションを同時更新する
- 不明値は推測せず空欄または `unknown` を使う
- セグメントが不明な場合でも、`notes` に「どこまで判別できたか」を残す
- 詳細な主観メモは、YAMLの `notes` または追加の補足キーとして残してよい
- 新規ログには、Garmin転記事実や取り込みメタデータと分けて `feedback` と `menu_decision` を追加する。既存ログへの一括バックフィルは不要
- `feedback` は簡潔な日本語で、実施内容、予定との差、根拠のある良い点・注意点、同種の直近比較、次回への意味を残す
- `menu_decision.outcome` は `keep` / `adjust` / `defer` のいずれかとし、事実、解釈、仮説、根拠ログ、反証確認、再評価条件を区別する
- `menu_decision.status` は回答待ちの `pending_user_input` と確定済みの `final` を区別する。`pending_user_input` では `outcome` を無理に確定しない
- 正本判断と次回行動を分け、`next_session_action` は `maintain` / `trial_one_step` / `reduce` / `stop` を使う。正本を維持して次回だけ試す場合は `outcome: keep` と `next_session_action: trial_one_step` を併記する
- 比較は原則として直近8週間の同種セッションを新しい順に最大3件使う。比較対象が1件しかない通常結果をトレンドと呼ばない
- 恒久的な `adjust` は原則として少なくとも2回の比較可能な完遂セッションで同方向の根拠が続く場合に限る。痛みなど明確な安全上の懸念による単発の中止・保留・負荷低減は例外とする

追加キーの例:

```yaml
feedback:
  completed: "確認できた事実だけを書く。"
  positives: "今回ログまたはユーザ主観に結びつける。"
  concerns: "欠損や予定との差も明記する。"
  recent_comparison: "YYYY-MM-DDの同種ログと比較。比較不能なら理由を書く。"
  next_workout: "次回に維持・観察・回避する点。"
menu_decision:
  status: final
  outcome: keep
  next_session_action: maintain
  trial_targets: none
  fact: "直接確認できる事実。"
  interpretation: "事実から妥当に読めること。"
  hypothesis: "追加確認が必要な可能性。なければnone。"
  rationale: "判断理由と反証確認。"
  evidence:
    - "YYYY-MM-DD session_type"
  review_conditions: "判断を見直す条件。"
```

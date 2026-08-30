# Garmin Log Intake Template

Garmin画像からテキスト転記するときのテンプレートです。画像を見ながら、分かる範囲だけを正確に埋めます。推測はしません。

## セッション要約テンプレート

```yaml
date: YYYY-MM-DD
session_type: A_full | B_full | A_machine_only | B_machine_only | C_treadmill | treadmill_only | extra_treadmill
c_mode: recovery | standard | endurance | not_applicable
segment_type: full_session
duration_min:
avg_hr:
max_hr:
aerobic_te:
anaerobic_te:
exercise_load:
calories:
primary_benefit:
avg_temp:
zone1_time:
zone2_time:
zone3_time:
zone4_time:
zone5_time:
subjective_fatigue:
soreness_next_day:
machine_order_changed:
menu_deviation:
notes:
minimum_subjective:
  overall_load: light | appropriate | heavy | mixed
  muscle_soreness:
    status: none | light | strong
    areas: []
    timing: pre_session | post_session | next_day
  pain_or_form_issue:
    status: none | present
    details:
machine_adjustments:
  - machine:
    planned_weight_kg:
    actual_weight_kg:
    adjustment: one_step_heavier | one_step_lighter | other
    resolution_basis:
    subjective_comment:
subjective_notes:
  treadmill_feedback:
    selected_c_mode:
    selection_purpose:
    main_rpe:
    conversation_possible:
    actual_speed_and_incline:
    knee_pain_or_discomfort:
    next_day_impact_on_a_b_or_daily_activity:
  machine_feedback:
    lat_pulldown:
      last_set_reps_in_reserve:
      form_quality:
      target_muscle_feel:
    row_machine:
      last_set_reps_in_reserve:
      form_quality:
      target_muscle_feel:
    chest_press:
      last_set_reps_in_reserve:
      form_quality:
      target_muscle_feel:
    shoulder_press:
      last_set_reps_in_reserve:
      form_quality:
      target_muscle_feel:
    hip_adduction_inward:
      last_set_reps_in_reserve:
      form_quality:
      target_muscle_feel:
    hip_abduction_outward:
      last_set_reps_in_reserve:
      form_quality:
      target_muscle_feel:
    torso_rotation:
      last_set_reps_in_reserve:
      form_quality:
      target_muscle_feel:
    abdominal:
      last_set_reps_in_reserve:
      form_quality:
      target_muscle_feel:
  post_session:
    back_tightness_0_to_2:
    chest_tightness_0_to_2:
    shoulder_tightness_0_to_2:
    abdominal_tightness_0_to_2:
    treadmill_difficulty:
  next_day:
    soreness_areas:
    fatigue_level:
feedback:
  completed:
  positives:
  concerns:
  recent_comparison:
  next_workout:
menu_decision:
  status: pending_user_input | final
  outcome: keep | adjust | defer
  next_session_action: maintain | trial_one_step | reduce | stop
  trial_targets:
  fact:
  interpretation:
  hypothesis:
  rationale:
  evidence:
  review_conditions:
segments:
  - segment_type: warmup
    duration_min:
    avg_hr:
    max_hr:
    aerobic_te:
    anaerobic_te:
    exercise_load:
    calories:
    primary_benefit:
    notes:
  - segment_type: machine
    duration_min:
    avg_hr:
    max_hr:
    aerobic_te:
    anaerobic_te:
    exercise_load:
    calories:
    primary_benefit:
    notes:
  - segment_type: treadmill_main
    duration_min:
    avg_hr:
    max_hr:
    aerobic_te:
    anaerobic_te:
    exercise_load:
    calories:
    primary_benefit:
    notes:
  - segment_type: cooldown
    duration_min:
    avg_hr:
    max_hr:
    aerobic_te:
    anaerobic_te:
    exercise_load:
    calories:
    primary_benefit:
    notes:
  - segment_type: extra_treadmill
    duration_min:
    avg_hr:
    max_hr:
    aerobic_te:
    anaerobic_te:
    exercise_load:
    calories:
    primary_benefit:
    notes:
```

## 転記時のルール

- Garmin画像やユーザのテキストから確認できる値だけを埋める
- 分からない項目は空欄または `unknown`
- 通常の最小主観入力は `minimum_subjective` の負荷感、筋肉痛、運動中の痛み・明確なフォーム問題とする。詳細なreps・RIRは任意
- メニュー判断に必要な最小主観が欠けている場合は、ユーザへ1〜3問だけ短く確認する。未質問の欠損だけで `defer` にしない
- `session_type` は必ず分類ルールに従う
- `segments` は存在するものだけ残し、不要な雛形は削ってよい
- A/Bのマシンパート、後半トレッドミル、追加トレッドミルが分かるなら分割して記録する
- ユーザから明示的に指定がない限り、A60 / B60 のラップは `Lap 1 = warmup`、`Lap 2 = machine`、`Lap 3 = treadmill_main`、`Lap 4 = cooldown` として転記する
- 現行Cとして実施したログは `session_type = C_treadmill` とし、`c_mode = recovery | standard | endurance` を必ず記録する。ユーザから明示的な指定がない限り `Lap 1 = warmup`、`Lap 2 = treadmill_main`、`Lap 3 = cooldown` として転記する。C以外の任意のトレッドミルのみ実施は `treadmill_only` とし、`c_mode = not_applicable` とする
- Cの速度・傾斜は正本上の固定値ではない。ユーザ入力またはGarmin情報から確認できる実際の設定だけを記録し、不明なら推測しない
- CのCSV行では、専用列を追加せず `notes` に `c_mode: recovery | standard | endurance` を明記する。YAMLではトップレベルの `c_mode` に保存する
- `notes` に、画像ファイル名や転記時の補足を残してよい
- B日は `subjective_notes` をできるだけ埋める
- ヒップマシンは裸の `hip_abduction` / `Hip Abduction` を使わず、内向きは `hip_adduction_inward` / `Hip Adduction (Inward / 内向き)`、外向きは `hip_abduction_outward` / `Hip Abduction (Outward / 外向き)` と記録する
- ユーザ入力や画像から方向を特定できない場合は、どちらかへ推測で割り当てず `hip_abduction_direction_unknown` とし、元表現を `notes` に残す
- 手動ラップを使う場合は、cooldown に入るとき負荷を下げた瞬間にラップを切る
- 「1段重い」「1段軽い」「次の重量」「ピンを1つ上/下」などの相対重量表現がある場合は、`data/menus/current-menus.md` の現行メニュー重量と、対象マシンの `data/machines/weight-options/*.md` の表示重量順を照合する
- 相対重量を一意に解決できる場合は、`unknown` にせず具体重量を記録する。これは推測ではなく、レポジトリ内の参照情報からの確定値として扱う
- 相対重量を解決した場合は、`machine_adjustments` に対象マシン、予定重量、実施重量、増減種別、根拠、体感を残す。単発ログの実施重量変更だけで現行メニューは更新しない
- 相対重量を一意に解決できない場合は、元の相対表現と未解決理由を `notes` に残す

## 取り込み後の必須フィードバック

新規ログの取り込みは、CSV/YAMLへの事実保存だけでは完了しない。別のレビュー依頼を待たず、次も同じ作業で行う。

1. `data/menus/current-menus.md` と `data/menus/design-philosophy.md` で予定メニューとA/B/Cの評価軸を確認する
2. `sessions.csv` と `sessions.yaml` から、直近8週間の同種セッションを新しい順に最大3件確認する
3. AはA、BはB、Cは同じ `c_mode` の `C_treadmill` 同士、同じマシン、同等のトレッドミル処方を優先して比較する
4. 今回の事実、解釈、仮説、反証またはデータ限界を分ける
5. `feedback` に、完遂内容、予定との差、良い点、注意点、日付つき直近比較、次回への意味を簡潔な日本語で保存する
6. `menu_decision.outcome` を `keep` / `adjust` / `defer` から1つ選び、根拠と再評価条件を保存する
7. 正本判断と分けて `next_session_action` を決める。正本を維持した次回試行は `outcome: keep`、`next_session_action: trial_one_step` とする
8. 判断に必要なクリティカル情報が欠ける場合は `status: pending_user_input` と質問を保存し、回答後に `status: final` として判断を確定する
9. 同じフィードバックと判断の要点をユーザへ日本語で返す

`feedback` はGarmin転記値や取り込み元メモとは別の解釈レイヤーである。一般的な称賛は避け、各結論を今回ログ、ユーザコメント、または日付つき比較ログへ結びつける。

恒久的な `adjust` は、原則として直近8週間の少なくとも2回の比較可能な完遂セッションで同方向の根拠が続き、重大な反証がなく、具体的な変更値を確定できる場合だけにする。反復する「軽い」という所感と問題なしの簡易主観があれば、詳細なreps・RIRがなくても次回試行を提案できる。通常の単発結果は正本変更とせず、必要に応じて `keep + trial_one_step` とする。明示的な痛みや異常症状など安全上の懸念は単発でも中止、保留、負荷低減の根拠にできるが、安定トレンドとは呼ばない。

Cはモード選択理由、完遂状況、実際の速度・傾斜、RPE、会話可能性、心拍推移、膝・局所疲労、翌日疲労を評価する。速度・傾斜は所定時間を目標RPEで完遂するための調整値として扱う。Cを恒久変更する場合も、同じ `c_mode` の比較可能な完遂2回以上を原則とし、モードの時間または目標RPEの主な1項目だけを変更する。

`adjust` の場合は、最小の1次元だけを変更し、`README.md`、`data/menus/current-menus.md`、`data/menus/menu-history.md` を同期する。履歴にはprevious/new version、before/after、日付つき根拠、理由、意図する効果、再評価条件、rollbackまたは再検討条件を残す。

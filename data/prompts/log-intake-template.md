# Garmin Log Intake Template

Garmin画像からテキスト転記するときのテンプレートです。画像を見ながら、分かる範囲だけを正確に埋めます。推測はしません。

## セッション要約テンプレート

```yaml
date: YYYY-MM-DD
session_type: A_full | B_full | A_machine_only | B_machine_only | treadmill_only | extra_treadmill
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
machine_adjustments:
  - machine:
    planned_weight_kg:
    actual_weight_kg:
    adjustment: one_step_heavier | one_step_lighter | other
    resolution_basis:
    subjective_comment:
subjective_notes:
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
  outcome: keep | adjust | defer
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
- `session_type` は必ず分類ルールに従う
- `segments` は存在するものだけ残し、不要な雛形は削ってよい
- A/Bのマシンパート、後半トレッドミル、追加トレッドミルが分かるなら分割して記録する
- ユーザから明示的に指定がない限り、A60 / B60 のラップは `Lap 1 = warmup`、`Lap 2 = machine`、`Lap 3 = treadmill_main`、`Lap 4 = cooldown` として転記する
- `notes` に、画像ファイル名や転記時の補足を残してよい
- B日は `subjective_notes` をできるだけ埋める
- 手動ラップを使う場合は、cooldown に入るとき負荷を下げた瞬間にラップを切る
- 「1段重い」「1段軽い」「次の重量」「ピンを1つ上/下」などの相対重量表現がある場合は、`data/menus/current-menus.md` の現行メニュー重量と、対象マシンの `data/machines/weight-options/*.md` の表示重量順を照合する
- 相対重量を一意に解決できる場合は、`unknown` にせず具体重量を記録する。これは推測ではなく、レポジトリ内の参照情報からの確定値として扱う
- 相対重量を解決した場合は、`machine_adjustments` に対象マシン、予定重量、実施重量、増減種別、根拠、体感を残す。単発ログの実施重量変更だけで現行メニューは更新しない
- 相対重量を一意に解決できない場合は、元の相対表現と未解決理由を `notes` に残す

## 取り込み後の必須フィードバック

新規ログの取り込みは、CSV/YAMLへの事実保存だけでは完了しない。別のレビュー依頼を待たず、次も同じ作業で行う。

1. `data/menus/current-menus.md` と `data/menus/design-philosophy.md` で予定メニューとA/Bの評価軸を確認する
2. `sessions.csv` と `sessions.yaml` から、直近8週間の同種セッションを新しい順に最大3件確認する
3. AはA、BはB、同じマシン、同等のトレッドミル処方を優先して比較する
4. 今回の事実、解釈、仮説、反証またはデータ限界を分ける
5. `feedback` に、完遂内容、予定との差、良い点、注意点、日付つき直近比較、次回への意味を簡潔な日本語で保存する
6. `menu_decision.outcome` を `keep` / `adjust` / `defer` から1つ選び、根拠と再評価条件を保存する
7. 同じフィードバックと判断の要点をユーザへ日本語で返す

`feedback` はGarmin転記値や取り込み元メモとは別の解釈レイヤーである。一般的な称賛は避け、各結論を今回ログ、ユーザコメント、または日付つき比較ログへ結びつける。

恒久的な `adjust` は、原則として直近8週間の少なくとも2回の比較可能な完遂セッションで同方向の根拠が続き、重大な反証がなく、具体的な変更値を確定できる場合だけにする。通常の単発結果は `keep` または `defer` とする。明示的な痛みや異常症状など安全上の懸念は単発でも中止、保留、負荷低減の根拠にできるが、安定トレンドとは呼ばない。

`adjust` の場合は、最小の1次元だけを変更し、`README.md`、`data/menus/current-menus.md`、`data/menus/menu-history.md` を同期する。履歴にはprevious/new version、before/after、日付つき根拠、理由、意図する効果、再評価条件、rollbackまたは再検討条件を残す。

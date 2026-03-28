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

- 画像で読める値だけを埋める
- 分からない項目は空欄または `unknown`
- `session_type` は必ず分類ルールに従う
- `segments` は存在するものだけ残し、不要な雛形は削ってよい
- A/Bのマシンパート、後半トレッドミル、追加トレッドミルが分かるなら分割して記録する
- ユーザから明示的に指定がない限り、A60 / B60 のラップは `Lap 1 = warmup`、`Lap 2 = machine`、`Lap 3 = treadmill_main`、`Lap 4 = cooldown` として転記する
- `notes` に、画像ファイル名や転記時の補足を残してよい
- B日は `subjective_notes` をできるだけ埋める
- 手動ラップを使う場合は、cooldown に入るとき負荷を下げた瞬間にラップを切る

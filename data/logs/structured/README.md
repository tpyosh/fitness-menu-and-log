# Structured Garmin Logs

このディレクトリでは、Garmin画像から転記した内容を構造化して保持します。

## 使い分け

- `sessions.csv`
  - 1行1セッションの一覧表
  - 日付、分類、主要Garmin指標、メモを素早く見返すために使う
- `sessions.yaml`
  - 1セッションごとの詳細記録
  - ラップ情報、主観メモ、メニュー逸脱、補足説明を残すために使う

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

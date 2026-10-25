# Structured Garmin Logs

このディレクトリでは、Garmin画像やGarmin Connectの画面から読み取った内容を構造化して保持します。

## 使い分け

- `sessions.csv`
  - 1行1セッションの一覧表
  - 日付、分類、主要Garmin指標、メモを素早く見返すために使う
  - Cでは `notes` に `c_mode: recovery | standard | endurance` を明記する
- `sessions.yaml`
  - 1セッションごとの詳細記録
  - ラップ情報、主観メモ、メニュー逸脱、補足説明に加え、取り込み後のフィードバックとメニュー判断を残すために使う
  - Cではトップレベルの `c_mode` を必須とする

## 処方・差分・実施基準

実施日の処方は `data/menus/prescriptions.json` の `effective_from` で解決する。最新の完全版は `data/menus/current-menus.md`、一回限りの試行状態は `data/menus/active-trials.json` を見る。処方スナップショットが見つからない日付や、A/B/C・Cモードが確定しない場合、現行メニューを過去へ無条件に当てはめない。

A60/B60/Cの実施申告は原則として処方への差分入力とする。手順は以下の順序で適用する。

1. 処方IDと種目・区間・参考重量・回数範囲・set数・速度・傾斜・時間を読む。
2. 有効な次回限定試行があれば通常参考重量と分けて確認する。試行を見送った申告も差分として記録し、試行状態を閉じる。
3. ユーザの明示的な変更・省略・一部set変更を、その項目だけ上書きする。
4. Garmin等の直接観測値を対応する項目に重ねる。異なる直接観測同士の矛盾は勝手に解消しない。GarminのTotal Sets 1等、種目別実績を表さない集計は元表示として別に保持する。
5. `prescribed_workout`、`reported_deviations`、`effective_execution`と各値の`provenance`をYAMLに残す。処方を継承した値は `prescribed_no_deviation_reported`、本人が確認した値は`user_reported`などとする。

処方の8〜12回は実際に12回した証拠ではない。処方由来の`sets: 2`も直接観測した2setとは区別する。ユーザが「上限回数まで」と答えた場合に初めて、その範囲で回数を確定する。Garminに重量がないことだけを理由に毎回重量を聞き直さない。メニューそのものが不明、複数処方が競合、観測値が矛盾する、または安全・次回判断を変える欠損がある場合だけ質問する。

## Garminから読み取る項目

以下は取得対象であり、全項目がそろうことは取り込みの条件ではない。時間・心拍・TE・負荷・カロリー等の読めた主要値から保存を進める。ラップ・ゾーンや主要値の一部が欠けても、対象と分類が確定できれば取り込める。

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

## ユーザの主観入力（任意）

詳細なreps・RIRを含め、次の主観は本人申告がある範囲で残す。毎回の質問票にはしない。

- 全体または種目別の負荷感: `軽い` / `適正` / `重い` / `混在`
- 筋肉痛: `なし` / `軽い` / `強い` と部位
- 運動中の痛みまたは明確なフォーム問題: `なし` / `あり` と内容

対象の取り違え、記録分類に必要なメニュー特定、安全や次回判断が実質的に変わる情報だけ、既存文脈で補えなければ1〜3問に絞る。主観の欠損は事実保存を止めず、未申告を「痛みなし」「筋肉痛なし」としない。小さな欠損は限界と再評価条件を添え、重要な判断だけ `pending_user_input` とする。未質問の欠損を理由に `defer` としない。

## セッション分類ルール

- `A_full`
  - Aマシン + トレッドミルを実施した正規A日
- `B_full`
  - Bマシン + トレッドミルを実施した正規B日
- `A_machine_only`
  - Aのマシンのみで終了した短縮版
- `B_machine_only`
  - Bのマシンのみで終了した短縮版
- `C_treadmill`
  - 現行のCメニューとして傾斜トレッドミルだけを実施した日。`c_mode` に `recovery` / `standard` / `endurance` のいずれかを必ず記録する
- `treadmill_only`
  - Cとして指定されていない任意のトレッドミルだけの日
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

Cは、ユーザから明示的な指定がない限り次の3ラップとして扱う。

- `Lap 1`: `warmup`
- `Lap 2`: `treadmill_main`
- `Lap 3`: `cooldown`

## C日で参考にする主観メモ（申告がある範囲）

- 選択した `c_mode` と、そのモードを選んだ目的
- ウォームアップ、メイン、クールダウンの予定速度・傾斜と、実際に使った速度・傾斜
- メインのきつさ: RPEまたは `楽` / `適正` / `きつい`
- メイン中に会話できたか
- 運動中の膝痛・明確な違和感の有無
- 翌日の疲労がA/Bや日常活動へ影響したか

これらを毎回すべて質問せず、現在の判断に必要な部分だけ確認する。未申告の翌日反応を先回りして求めない。

Cのログも取り込み後のフィードバックループの対象とし、直近8週間の同じ `c_mode` にある比較可能な `C_treadmill` を新しい順に最大3件確認する。速度・傾斜はモードごとの初期処方と実績を比較し、目標RPEを外れた場合の下方調整も残す。比較可能な完遂2回以上で同方向の根拠が続くまでは、通常の単発結果だけでモードの時間、速度、傾斜、目標RPEを恒久変更しない。

Cの `feedback.next_workout` と `menu_decision` には、次回同モードの時間・速度・傾斜を具体的に書く。現行値を維持する場合も `maintain` と数値を明記し、次回だけ変える場合は `keep + trial_one_step` または `keep + reduce` と `trial_targets` を残す。痛みなど安全上の懸念では単発でも `reduce` または `stop` を選べる。

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
  - 現行Cとして実施した場合は `session_type = C_treadmill`
  - Cではない任意実施は `session_type = treadmill_only`
- 追加トレッドミル版
  - A/B後に別枠で実施した場合は `extra_treadmill` として記録する

## 更新時の注意

- CSVとYAMLは同じセッションを同時更新する
- 不明値は推測せず、CSVの数値は空欄、YAMLの数値は空欄（`null`）にする。文字・主観は既存形式の空欄または `unknown` を使う。未取得を0にしない
- セグメントが不明な場合でも、`notes` に「どこまで判別できたか」を残す
- 詳細な主観メモは、YAMLの `notes` または追加の補足キーとして残してよい
- 新規ログには、Garmin転記事実や取り込みメタデータと分けて `feedback` と `menu_decision` を追加する。既存ログへの一括バックフィルは不要
- `feedback` は簡潔な日本語で、実施内容、予定との差、根拠のある良い点・注意点、同種の直近比較、次回への意味を残す
- `menu_decision.outcome` は `keep` / `adjust` / `defer` のいずれかとし、事実、解釈、仮説、根拠ログ、反証確認、再評価条件を区別する
- `menu_decision.status` は回答待ちの `pending_user_input` と確定済みの `final` を区別する。`pending_user_input` では `outcome` を無理に確定しない
- 正本判断と次回行動を分け、`next_session_action` は `maintain` / `trial_one_step` / `reduce` / `stop` を使う。正本を維持して次回だけ試す場合は `outcome: keep` と `next_session_action: trial_one_step` を併記する
- 比較は原則として直近8週間の同種セッションを新しい順に最大3件使う。比較対象が1件しかない通常結果をトレンドと呼ばない
- 恒久的な `adjust` は原則として少なくとも2回の比較可能な完遂セッションで同方向の根拠が続く場合に限る。痛みなど明確な安全上の懸念による単発の中止・保留・負荷低減は例外とする

## Garmin Connectの取得元と重複確認

CSV列や必須キーは増やさず、CSV/YAML双方の既存 `notes` に取得元を同じ内容で残す。例（未取得の値をコピーしない）:

```yaml
notes: "garmin_activity_id=123456789; garmin_url=https://connect.garmin.com/app/activity/123456789; fetched_at=2026-10-25T22:30:00+09:00; start_time=10:18; garmin_type=Cardio; duration_display=1:16:46; missing=laps,zones,max_hr"
```

- `fetched_at` は実際に取得した日時（Asia/Tokyo）。読めない開始時刻・種目・表示時間は省略し、IDやURL自体が未確認なら捏造しない。`missing` は取得を試みたが読めない項目や未取得の画面を簡潔に記す。網羅的な欠損一覧や別管理ファイルは作らない。
- 追加前に `sessions.csv` と `sessions.yaml` のactivity ID・URLを検索する。同じIDがあれば記録済みとして新規追加せず、元ログを保持する。再取得できただけで過去ログを上書きしない。
- IDのない過去ログも、日付・開始時刻・種目・時間・心拍・カロリー・本人申告を読めた範囲で照合する。ID欠損だけを理由に追加しない。十分一致する既存セッションなら記録済みとして終え、IDの追記も必須にしない。
- 区別できない候補がある場合は追加だけ止め、候補を区別する短い1問にする。同じ日・同じ `session_type` は既存のCSV/YAML一意キーでもある。別activityでもこのキーが衝突する場合は無理に追加・統合せず、取得結果を返して分類を確認する。
- `duration_min` は読めた時間を分へ換算し、既存精度に合わせる。正確な表示時間は `duration_display` に残せる。ラップ・ゾーン合計との差は表示値のまま短く注記し、原因・補正値を作らない。ラップ未取得なら架空の `segments` を作らず、省略または空配列とする。

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

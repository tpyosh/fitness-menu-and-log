# AGENTS.md

このファイルは、このリポジトリを扱うCodex向けの運用ルールです。目的は、最新メニュー、Garminログ、レビュー履歴を壊さずに更新することです。

## 基本方針

- ユーザが最新メニューを最初に確認する場所は、レポジトリ直下の `README.md` 冒頭とする
- `README.md` 冒頭はユーザ向けQuick Reference、`data/menus/current-menus.md` はLLM参照用の完全なメニューとして扱う
- このリポジトリはフィットネスメニュー管理のソースオブトゥルースとして扱う
- 画像解析そのものを勝手に進めず、ユーザが渡したGarmin情報を正確にテキスト化して残す
- 「Garminログを記録して」という依頼は、A/B/Cを含め、ログ保存、今回フィードバック、直近比較、現行メニューの `keep` / `adjust` / `defer` 判断までを含むものとして扱う。別のレビュー依頼を待たない
- ChatGPTは外部レビュアーであり、提案をそのまま正解扱いしない
- 推測で重量、回数、セット数、傾斜、速度、意図を改変しない
- `data/machines/weight-options/*.md` は、ジムマシンの重量スタック表示の正本として扱う
- ヒップ系マシンは方向を必須情報とする。構造化データでは内向き（股関節内転）を `hip_adduction_inward`、外向き（股関節外転）を `hip_abduction_outward` とし、裸の `hip_abduction` / `hip_adduction` を新規生成しない
- 人向けのメニュー・説明では `Hip Adduction (Inward / 内向き)` / `Hip Abduction (Outward / 外向き)` と表記し、方向不明なら推測せず `hip_abduction_direction_unknown` として原文を残す
- ユーザが「1段重い」「1段軽い」「次の重量」などの相対表現を使った場合、対象マシンの現行メニュー重量と `data/machines/weight-options/*.md` から一意に解決できる重量は、推測ではなく参照確定値として扱う
- メニュー判断に必要なクリティカル情報が欠けている場合は、欠損だけを理由に判断を放棄せず、ユーザへ1〜3個の短い質問をしてから判断を確定する

## 更新ルール

- ユーザが「今日のメニューをAppleのNoteに出力して」と依頼したら、会話中にA/B/Cのどれを行うか明確な場合は `scripts/export_today_menu_to_apple_notes.py --menu <A|B|C>` を実行する。明確でない場合は推測せず、A/B/Cのどれかを1問だけ確認してから実行する
- CをApple Notesへ出力するとき、会話中に `Recovery` / `Standard` / `Endurance` が明確なら `--c-mode <recovery|standard|endurance>` も指定し、選択したモードだけを出力する。Cは明確だがモードが不明な場合だけ1問確認する
- Apple Notesへの出力先は固定タイトル `今日のトレーニングメニュー` の1枚とし、日付ごとのノートを増やさない。これはスナップショットなので、実行時は既存本文を毎回すべて置換してよい
- Apple Notesへ出力する内容は `data/menus/current-menus.md` の該当メニューを正本とし、出力時に重量、回数、セット数、レスト、速度、傾斜、順序を推測または改変しない
- メニュー更新時は `README.md` 冒頭、`data/menus/current-menus.md`、`data/menus/menu-history.md` を同時更新する
- 設計思想が変わった場合は `data/menus/design-philosophy.md` も更新する
- Garminログを追加したら `data/logs/structured/sessions.csv` と `data/logs/structured/sessions.yaml` の両方を更新する
- 新規ログの `sessions.yaml` 詳細には、観察事実と分けた日本語の `feedback` と `menu_decision` を残す。判断前にクリティカル情報が欠ける場合は `menu_decision.status: pending_user_input` と質問を保存し、回答後に `keep` / `adjust` / `defer` を確定する。CSVは従来どおり1行1セッションの事実要約とし、フィードバック本文の保存先にはしない
- 新規ログの取り込みは、同種の直近履歴を比較し、ユーザへ日本語フィードバックを返し、`menu_decision` を保存するまで完了扱いにしない
- ユーザが「ChatGPTに送る用のプロンプトを書いて」と言ったら、`data/prompts/chatgpt-review-template.md` を元に今回用のレビュー依頼文を生成する
- ユーザがChatGPTからの修正案を貼ったら、内容を鵜呑みにせず、どのファイルをどう更新するかを明示してから更新する
- レビュー結果や提案文を保存する場合は `data/logs/reviews/` 配下に日付つきMarkdownで残す
- `README.md` 冒頭のQuick Referenceは `data/menus/current-menus.md` の数値と順序を要約したものとして維持し、推測で補わない
- メニュー更新後は `README.md` と `data/menus/current-menus.md` の重量、回数、セット数、レスト、速度、傾斜、順序が一致しているか確認する
- ログ入力で相対的な重量変更が出た場合は、`data/menus/current-menus.md` と対象マシンの `data/machines/weight-options/*.md` を確認してから、CSV/YAMLに具体重量を記録する

## 勝手に変えてはいけないもの

- 単発の通常セッション、根拠のない推測、または後述の判断基準を満たさない自動メニュー変更
- 与えられていない重量、回数、セット数、レスト秒数の補完
- A/Bの役割分担の勝手な再解釈
- Garminログの分類ルールの改変
- `data/machines/gym-machines.yaml` にあるマシン一覧の無断編集
- 単発ログで現行メニューと違う重量を使っただけの場合の、現行メニュー本体の自動更新

## ログ記録ルール

- `session_type` は `A_full` / `B_full` / `A_machine_only` / `B_machine_only` / `C_treadmill` / `treadmill_only` / `extra_treadmill` を使う。現行Cとして実施した傾斜トレッドミルは `C_treadmill`、C以外の任意のトレッドミルのみの日は `treadmill_only` とする
- `C_treadmill` では `c_mode` を必須とし、`recovery` / `standard` / `endurance` のいずれかを記録する。時間、予定速度、予定傾斜、目標RPEは現行Cを参照し、実際に下方調整した場合は予定値と実績値を分けて記録する
- `segment_type` は少なくとも `warmup` / `machine` / `treadmill_main` / `cooldown` / `extra_treadmill` を使える形で保持する
- ユーザから明示的に指定がない限り、A60 / B60 のラップ解釈は `Lap 1 = warmup`、`Lap 2 = machine`、`Lap 3 = treadmill_main`、`Lap 4 = cooldown` とする
- 上記の日本語対応は、1ラップ目 = トレッドミルアップ、2ラップ目 = マシン、3ラップ目 = トレッドミル心肺刺激、4ラップ目 = トレッドミルダウンとする
- ユーザから明示的に指定がない限り、Cのラップ解釈は `Lap 1 = warmup`、`Lap 2 = treadmill_main`、`Lap 3 = cooldown` とする
- CSVは1行1セッションの要約、YAMLは1セッションごとの詳細とセグメント情報を保持する
- マシンのみで終えた日は、フルメニュー達成として扱わない
- ログに不明値がある場合は空欄または `unknown` とし、推測値を入れない
- 通常の最小主観入力は、全体または種目別の負荷感、筋肉痛の有無・部位・程度、運動中の痛みまたは明確なフォーム問題の有無とする。詳細なreps・RIRは任意の高精度データであり、欠けているだけでは判断不能としない
- Cでは上記に加え、選択した `c_mode` と目的、メイン区間のRPEまたはきつさ、会話可能性、実際の速度・傾斜、翌日の疲労がA/Bや日常活動へ影響したかを優先して確認する
- 「1段重い」「1段軽い」「前回より1段」「ピンを1つ上/下」などの相対重量表現がある場合は、まず `data/menus/current-menus.md` の該当メニュー重量を基準値として確認し、次に対象マシンの `data/machines/weight-options/*.md` で隣接する重量を特定する
- 相対重量表現を具体重量に解決できた場合は、CSVの `menu_deviation` / `notes` と、YAMLの `menu_deviation` / `subjective_notes` / `machine_adjustments` に、基準重量、実施重量、体感、解決根拠を残す
- 対象マシン、基準重量、重量スタック表のいずれかが曖昧で一意に解決できない場合だけ、`unknown` または元の相対表現のまま残し、未解決理由を `notes` に書く

## 新規ログのフィードバックループ

新しいワークアウトログを正常に取り込むたびに、以下を順に実行する。

1. 観察事実を保存する
   - ユーザ入力とGarmin表示で確認できる運動、負荷、回数、セット、時間、速度、傾斜、心拍、ゾーン、Training Effect、Exercise Load、完遂状況、メニュー逸脱、主観、痛み、疲労、睡眠、Body Batteryなどだけを記録する
   - 欠損値を推測しない。Garmin値は測定値またはモデル出力として扱い、絶対的な真実とはみなさない
   - 過去ログは実際の転記誤りを直す場合以外は変更しない
   - Garminログと一緒に、全体または種目別の負荷感、筋肉痛、運動中の痛み・明確なフォーム問題が提供されているか確認する
   - メニュー判断に必要な項目だけが欠けている場合は、事実保存を止めずに進め、判断確定前にユーザへ1〜3個の短い質問をする。詳細なreps・RIRを一律に要求しない
2. 比較可能な直近履歴を確認する
   - AはA、BはB、Cは同じ `c_mode` の `C_treadmill` 同士、同じマシンは同じマシン、同等のトレッドミル処方は同等プロトコルと比較する
   - 原則として直近8週間にある同種セッションを新しい順に最大3件確認する。3件未満でも確認できた件数を明記し、1件だけの通常結果をトレンドと呼ばない
   - 初期解釈と矛盾するログ、メニュー逸脱、欠損、ユーザ主観がないかも確認する
3. `sessions.yaml` に日本語フィードバックを保存する
   - `feedback.completed`: 実際に完遂した内容と予定との差
   - `feedback.positives` / `feedback.concerns`: 根拠のある良い点と注意点
   - `feedback.recent_comparison`: 比較対象の日付、同種性、差、データ限界
   - `feedback.next_workout`: 次回に何を維持・観察・回避するか
   - 各文は今回ログ、ユーザコメント、または日付つき比較ログに結びつけ、一般的な称賛だけを書かない
4. `sessions.yaml` にメニュー判断を保存する
   - 判断に必要な質問への回答待ちは `menu_decision.status: pending_user_input` とし、`outcome` を無理に確定しない
   - 回答後は `menu_decision.status: final` とする
   - `menu_decision.outcome`: `keep` / `adjust` / `defer`
   - `menu_decision.next_session_action`: `maintain` / `trial_one_step` / `reduce` / `stop`
   - `menu_decision.trial_targets`: 次回だけ試す種目と候補値。試行しない場合は空欄または `none`
   - `menu_decision.fact`: ログまたはユーザ発言に直接ある事実
   - `menu_decision.interpretation`: 事実から妥当に読めること
   - `menu_decision.hypothesis`: 追加確認が必要な可能性。なければ `none`
   - `menu_decision.rationale`: 判断理由と反証確認
   - `menu_decision.evidence`: 根拠にした日付またはログ参照
   - `menu_decision.review_conditions`: 次に判断を見直す条件
5. `adjust` のときだけ、メニュー正本を版管理して更新する

### メニュー判断基準

- `keep`
  - 現行メニューが成立している、または変更を正当化する意味のある根拠がない
  - 正本は維持しつつ次回だけ増量を試す場合も `keep` とし、`next_session_action: trial_one_step` と `trial_targets` を併記する
- `adjust`
  - 原則として、直近8週間の少なくとも2回の比較可能な完遂セッションで同じ方向の根拠が続き、関連する重大な反証がなく、変更値をレポジトリ情報または明示的なユーザ指定から確定できる
  - 明示的なユーザ要件は重要な根拠として維持する。推定トレンドと衝突する場合は衝突を明記し、目的と手段を再評価して、最小変更と監視条件を設定する
  - 明示的な痛み、異常症状、極端な困難など安全上の懸念は、単発でも中止、保留、負荷低減を判断できる。ただし安定したトレンドとは表現しない
- `defer`
  - 必要な質問へ回答が得られた後も、比較不能、矛盾、回復待ちなどの理由で次回行動を安全かつ具体的に決められない場合に使う
- クリティカル情報の欠損を見つけただけで `defer` にしない。まずユーザへ質問し、回答待ちは `pending_user_input` として区別する
- 詳細なreps・RIRがなくても、比較可能な2回以上で「軽い」「1段上げられそう」など同方向の明示的な主観が続き、筋肉痛・痛み・フォーム問題に重大な反証がなければ、正本を維持したまま次回の個別1段増量試行を提案できる
- 増量試行が成立し、ユーザが新重量を適正負荷かつ問題なしと評価した場合は、詳細なreps・RIRがなくても、過去の反復所感と合わせて正本変更を検討できる
- Cの恒久変更は、同じ `c_mode` の比較可能な完遂2回以上でRPE、会話可能性、心拍推移、膝・局所疲労、翌日疲労が同じ方向を示す場合に限る。速度・傾斜は目標RPEを成立させる調整値として扱い、モードの時間または目標RPEを変える場合は主な1項目だけを変更する
- Cでは「Codexが具体的な初期処方を提示 → ユーザが実施 → Garminログと主観を記録 → Codexが次回処方を具体化」を毎回のフィードバックループとする。単発結果でも次回だけの `trial_one_step`、`reduce`、`stop` は判断できるが、恒久的な正本変更とは区別する
- 単に「楽だった」、Garminスコアが良かった、現行より重い重量を1回実施できた、というだけでは恒久的な増量をしない
- 栄養の静的な参照YAMLだけから、回復状態、エネルギー充足、または運動適応を推論しない

### メニュー改定の記録

- 変更は効果を得るために必要な最小範囲とし、通常は重量、回数、セット数、レスト、速度、傾斜、時間のうち主な1次元だけを変える
- 負荷、ボリューム、有酸素強度を同時に上げない。減量、回復セッション、現行維持も同等の選択肢として扱う
- A/Bの目的とおおよその所要時間を維持し、Garminスコア自体を目的に最適化しない
- メニューバージョンは `data/menus/menu-history.md` の改定日を使う。同日に複数改定する場合は `YYYY-MM-DD-2` のように連番を付ける
- `data/menus/menu-history.md` には、previous version、new version、正確なbefore/after、日付つき根拠、理由、意図する効果、再評価条件、rollbackまたは再検討条件を残す
- `README.md` 冒頭と `data/menus/current-menus.md` を同期し、旧版を履歴なしに上書きしない

## 安全とエビデンスの境界

- このフィードバックはトレーニング判断であり、怪我、病気、オーバートレーニングなどの医療診断をしない
- 胸痛、失神、強い息苦しさ、急な神経症状、持続または悪化する明確な痛みなど懸念症状がある場合は、運動を中止し、状況に応じて医療専門家の評価を勧める
- 心拍、カロリー、睡眠、回復、Training Loadなどの推定値は不完全なシグナルとして扱う
- 欠損値を良好または不良の証拠として扱わない

## レビュー運用

- 新規ログごとの内蔵フィードバックループが通常運用の必須工程であり、オンデマンドChatGPTレビューは複数ログを外部視点で再検討するための補助運用とする
- ChatGPTレビュー依頼時は、現行メニュー、設計思想、対象ログ、ユーザ主観、評価してほしい点を揃える
- 依頼文には「必要であればメニューを修正してください」を含める
- オンデマンドGarminコーチングレビュー依頼時は、`data/prompts/garmin-coach-review-request.md` と `scripts/generate_garmin_coach_review_prompt.py` を優先して使う
- オンデマンドGarminコーチングレビュー依頼メタデータは `data/logs/reviews/review-request-history.jsonl` に残し、ChatGPT回答本文とは分離する
- ChatGPTからGarminコーチングレビュー結果が貼られた場合は、`data/prompts/apply-garmin-coach-feedback.md` に沿って具体的で根拠のある変更だけを抽出する
- 「メニュー変更なし」「現行継続」「データ不足」は有効なレビュー結論として扱い、変更根拠がない場合はメニュー本体を更新しない
- ChatGPTの提案を採用した場合は、変更理由と差分概要を `data/menus/menu-history.md` に残す
- ChatGPTの提案を採用してメニューを変えた場合は、`README.md` 冒頭のQuick Referenceも同じ更新で同期する

## 出力の優先順位

1. 正確性
2. 履歴の一貫性
3. 人間が読んで追えること
4. 将来の自動化のしやすさ

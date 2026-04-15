# ChatGPT Review Template

以下は、CodexがChatGPTにレビューを依頼するときのテンプレートです。`{{ }}` を今回の内容で埋めて使います。

## テンプレート

```md
以下は、現在運用しているフィットネスメニュー管理情報です。
必要であればメニューを修正してください。
ただし、あなたの最終出力はユーザ向けの説明文ではなく、Codexにそのまま渡せる更新指示プロンプトにしてください。
あなた自身がファイルを更新した前提では書かず、Codexがこのリポジトリを更新する前提で書いてください。

# 1. 現在の設計思想

{{current_design_philosophy}}

# 2. 現在のA/Bメニュー

{{current_menus}}

# 3. 重量修正の候補レンジ

{{nearby_weight_options}}

# 4. 今回レビュー対象のログ

{{target_logs}}

# 5. ユーザの主観

{{user_subjective_notes}}

# 6. 評価してほしいこと

{{review_questions}}

# 7. 依頼

- 現在の設計思想に照らして、今回のログが狙い通りか評価してください
- A日/B日それぞれの評価軸に沿って見てください
- Garmin指標を過大評価しすぎず、主観や筋刺激も含めて判断してください
- 必要であればメニューを修正してください
- 重量を修正する場合は、現在値だけでなく、上に示した近傍候補のどれを採るかも明記してください
- 近傍候補の外を提案する場合は、その必要性も理由つきで明記してください
- 修正する場合は、どこをどう変えるか、理由つきで具体的に示してください

# 8. あなたの出力形式

- 最終出力は、Codexにそのまま貼り付けるためのMarkdownプロンプト本文だけを返してください
- ユーザ向けの前置き、感想、要約は付けず、Codexへの指示だけを書いてください
- まず、今回の結論を以下のように明示してください
  - `menu_update_required: yes/no`
  - `design_philosophy_update_required: yes/no`
- そのうえで、Codexに以下を指示してください
  - 今回のレビュー結論の要約
  - 更新対象ファイル
    - `README.md`
    - `data/menus/current-menus.md`
    - `data/menus/menu-history.md`
    - `data/menus/design-philosophy.md`（必要な場合のみ）
  - 各ファイルで何をどう変えるか
  - 採用する重量が候補レンジのどれか
  - 候補レンジ外を採る場合の理由
  - 推測で重量、回数、セット数、レスト、速度、傾斜を補わないこと
  - 更新後に `README.md` と `data/menus/current-menus.md` の数値・順序・A/B区分を一致確認すること
- メニュー更新が不要と判断した場合も、Codex向けプロンプトとして返してください
  - その場合は、メニュー更新不要の理由
  - 必要なら `data/logs/reviews/` にレビュー結果を保存すること
  - 今回は更新しないファイル
- 「更新済みです」「修正しました」のように、すでに反映した前提では書かないでください
```

## 差し込み時の注意

- `{{current_design_philosophy}}` には `data/menus/design-philosophy.md` の relevant 部分を入れる
- `{{current_menus}}` には `data/menus/current-menus.md` のA60 / B60を入れる
- `{{nearby_weight_options}}` には、現行メニューの重量に対して、`data/machines/weight-options/*.md` をSSOTとして近傍の選択肢を種目ごとに入れる
  - 形式は「現在値」と「近傍候補」が一目で分かる形にする
  - 候補は、重量スタックSSOTの前後値を基本にし、最近の実施実績やユーザ明示の重量があれば `note` で補足する
  - 現行メニュー重量がSSOTの表示値と完全一致する場合は、原則として「直近下 / 現在値 / 直近上」を入れる
  - 現行メニュー重量がSSOTの表示値と一致しない場合は、原則として「直近下 / 直近上 / その次の近傍」など、確認できた候補を並べたうえで、不一致を `note` に明記する
  - `weight-options` 側にファイルがない種目だけ、未確認として扱う
  - ChatGPTには、まずこの候補レンジ内で修正案を考えてもらい、必要ならレンジ外提案を補足してもらう
- `{{target_logs}}` には今回レビュー対象のセッション要約と必要なセグメント詳細を入れる
- `{{user_subjective_notes}}` には疲労感、張り、違和感、完遂感などを入れる
- `{{review_questions}}` には「A日の後半トレッドミル強度は妥当か」など、判断してほしい点を列挙する
- このテンプレートで期待するChatGPT出力は、レビュー本文そのものではなく、Codex向け更新プロンプト
- そのため、ChatGPTには「何をどう更新するか」「どのファイルを触るか」「更新不要なら何を保存するか」まで出力させる

## `{{nearby_weight_options}}` の書き方の目安

```md
## A日

- Seated Leg Press
  - current: 115kg
  - nearby options: 105kg / 115kg / 125kg
  - note: `data/machines/weight-options/seated-leg-press.md` に基づく

## B日

- Lat Pulldown
  - current: 33kg
  - nearby options: 26kg / 33kg / 40kg
  - note: `data/machines/weight-options/lat-pulldown.md` に基づく。40kgはユーザ実施あり

- Hip Adduction
  - current: 60kg
  - nearby options: 54kg / 61kg / 68kg
  - note: `data/machines/weight-options/hip-abduction-inward.md` に基づく。現行メニューの60kgとSSOT表示値61の差は要確認
```

上の数値は書き方の実例です。実際の差し込みでは、対象種目ごとに対応する `weight-options` ファイルを確認して埋めます。

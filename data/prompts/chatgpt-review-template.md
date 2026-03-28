# ChatGPT Review Template

以下は、CodexがChatGPTにレビューを依頼するときのテンプレートです。`{{ }}` を今回の内容で埋めて使います。

## テンプレート

```md
以下は、現在運用しているフィットネスメニュー管理情報です。
必要であればメニューを修正してください。

# 1. 現在の設計思想

{{current_design_philosophy}}

# 2. 現在のA/Bメニュー

{{current_menus}}

# 3. 今回レビュー対象のログ

{{target_logs}}

# 4. ユーザの主観

{{user_subjective_notes}}

# 5. 評価してほしいこと

{{review_questions}}

# 6. 依頼

- 現在の設計思想に照らして、今回のログが狙い通りか評価してください
- A日/B日それぞれの評価軸に沿って見てください
- Garmin指標を過大評価しすぎず、主観や筋刺激も含めて判断してください
- 必要であればメニューを修正してください
- 修正する場合は、どこをどう変えるか、理由つきで具体的に示してください
```

## 差し込み時の注意

- `{{current_design_philosophy}}` には `data/menus/design-philosophy.md` の relevant 部分を入れる
- `{{current_menus}}` には `data/menus/current-menus.md` のA60 / B60を入れる
- `{{target_logs}}` には今回レビュー対象のセッション要約と必要なセグメント詳細を入れる
- `{{user_subjective_notes}}` には疲労感、張り、違和感、完遂感などを入れる
- `{{review_questions}}` には「A日の後半トレッドミル強度は妥当か」など、判断してほしい点を列挙する

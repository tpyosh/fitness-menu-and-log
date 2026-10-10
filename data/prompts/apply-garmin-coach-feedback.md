# レビュー回答の反映テンプレート

```md
以下のChatGPTレビューを、現在の判断と課題バックログへ反映してください。

{{chatgpt_feedback}}

- AGENTS.mdとdata/logs/reviews/README.mdを守り、current-assessment.mdとbacklog.mdを先に読む。
- 提案を鵜呑みにせず、本人申告・Garmin観測・処方継承・推論を分けて正本へ照合する。
- 既存J-IDの判断・根拠・不確実性・再検討条件をその場で更新する。新しい判断だけ新規IDを付ける。
- 未解決の問いは既存B-IDへ統合し、優先度・次の確認・解決条件を更新する。新しい問いだけ新規IDを付ける。
- 解決には根拠と解決条件の成立が必要。同じ項目をresolvedにし、解決結果を記す。回答受領だけで閉じない。
- updated_on、出典名・直接URL・確認日・確認範囲・適用限界・情報の変動性、セッション・処方・試行IDを必要な箇所に残す。
- 回答全文や日付付きレビュー結果・採否メモ・統合メモは保存しない。依頼メタデータに回答本文を入れない。
- 根拠不足・変更不要・保留も有効な結果。推測で回数、症状、意図、重量、活動量を補わない。
- 通常処方と次回限定試行を区別し、レビューだけを理由に試行を重複作成したり恒久増量したりしない。
- 具体的な恒久改定が正当化される場合だけrevise-training-menuに従い、README冒頭・current-menus.md・menu-history.mdを同期する。処方数値変更はprescriptions.jsonへ新しい版を追加する。設計思想変更時だけdesign-philosophy.mdを更新する。
- 過去ログは根拠のある転記誤り以外では変更しない。ヒップ系の内向き／外向きとprovenanceを維持する。
- ruby scripts/validate_fitness_data.rbを実行する。コード変更時は適切な既存テストも実行する。
- 最後に、変更ファイル、J/B-IDごとの更新・維持・解決、未解決事項、検証結果を簡潔に報告する。
```

正本は`data/logs/reviews/current-assessment.md`と`data/logs/reviews/backlog.md`。メニュー実行値は従来のメニュー・処方・試行ファイルを参照する。

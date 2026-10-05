# 処方の正本と実施時点の解決

- `current-menus.md`: 最新の通常処方の完全な文章正本。参考重量、rep range、set、トレッドミル条件、フォーム指示を含む。
- `prescriptions.json`: 通常処方の版付き機械可読スナップショット。最新スナップショットは `current-menus.md` の「次回限定試行」表示を除いた本文のSHA-256と結び、両者がずれたら取り込みを止める。古いスナップショットは数値を上書きしない。
- `active-trials.json`: 次回だけの試行を管理する状態の正本。通常参考重量を変更しない。`current-menus.md` と `README.md` の試行欄は人向け表示であり、このJSONと同期する。
- `menu-history.md`: 改定理由と変更差分の履歴。過去処方の完全な機械可読スナップショットの代わりにはしない。

処方解決はセッション日付以前で最も新しい `effective_from` を選ぶ。対象日より前にスナップショットがない場合は、現在の処方を過去へ推測適用しない。最初のスナップショットは2026-08-31以降の通常A/B/Cを対象とし、通常処方の数値が2026-08-30のGit版`1d642ef`と一致することを照合した。これより古い日付は現在のJSONだけでは解決できない。

セッション取り込みでは、`scripts/workout_feedback.py` が通常処方→有効な次回限定試行→ユーザの明示的な差分→直接観測値の順で実施基準を組み立てる。`prescribed_no_deviation_reported` は直接観測した値とは別の根拠である。処方の回数範囲を実際の正確な回数へ変換しない。申告と観測が衝突した箇所だけ確認する。

次回限定試行は同じA/B/Cの次セッション1件にだけ適用する。そのセッションを記録したら `active-trials.json` の状態を `completed` / `declined` / `expired` に更新する。更新漏れがある場合は検証と次の処方解決を失敗させる。

処方を恒久変更するときは、通常の `README.md` / `current-menus.md` / `menu-history.md` の同期に加え、`prescriptions.json` に新しい版を追加し、`current_id`と`source_sha256`を更新する。`python3 scripts/workout_feedback.py --date YYYY-MM-DD --menu A --completed`で解決結果を確認し、`ruby scripts/validate_fitness_data.rb`とテストを実行する。

通常処方の数値・種目順・条件を変えず、説明文だけを直す場合は新しい処方版を作らず、最新版の`source_sha256`だけを更新して検証する。試行表示の変更は通常処方のハッシュに含まれない。

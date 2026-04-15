# Menu History

このファイルは、メニュー変更履歴の正本です。最新状態のQuick Referenceは `README.md` 冒頭、完全版は `current-menus.md` を見て、このファイルでは変更理由と差分概要を追います。

## 2026-04-11（ChatGPTレビュー採用）

- 種別: メニュー微修正
- 理由: 2026-03-28 から 2026-04-11 の直近ログと主観を踏まえたChatGPTレビューを採用し、B日の重量を最小限更新しつつ、A日はSSOT表記との不一致だけを正規化するため
- design philosophy update not required: yes
- 変更前:
  - A60 `Hip Adduction` は `60kg`
  - B60 `Lat Pulldown` は `33kg × 12回 × 4set`
  - B60 `Row Machine` は `33kg × 12回 × 4set`
  - B60 `Abdominal` は `35kg × 12回 × 3set`
- 変更後:
  - A60 `Hip Adduction` を `61kg × 12回 × 最大2set` に表記正規化
  - B60 `Lat Pulldown` を `40kg × 12回 × 4set` に更新
  - B60 `Row Machine` を `40kg × 12回 × 4set` に更新
  - B60 `Abdominal` を `42.5kg × 12回 × 3set` に更新
- 差分概要:
  - design philosophy は変更なし
  - A60 は実質据え置き
  - A60 `Hip Adduction` のみ、`data/machines/weight-options/hip-abduction-inward.md` の表示値に合わせて `61kg` 表記へ正規化
  - A日の 2026-04-09 は 2026-03-28 より有酸素主導として弱かったが、今回は処方変更ではなく様子見
  - A日 `Leg Press 115kg` と `Abdominal 42.5kg` は維持
  - B60 は `Lat Pulldown / Row Machine / Abdominal` を候補レンジ内で更新
  - B日の machine Avg HR は、主観的に限界近さが出ていれば致命的な問題とは扱わない方針を維持
  - B60 の実測 66〜72分は当面許容し、今回はレスト・種目数・トレッドミルは変更しない
  - 厳密に60分へ寄せたい要求が将来強くなった場合は、まず cooldown のばらつきと種目間移動の実測を揃えるべきであり、現段階で筋刺激側を削るべきではない
  - B60 という名称自体は変更しない
  - 不確実性:
    - 2026-04-09 `A_full` は主観メモ不足のため、A日の machine 側刺激妥当性は強く断定していない
    - 2026-04-11 `B_full` は翌日以降の張り・筋肉痛が未記録のため、今回の重量更新は最小限の前進として扱う
    - Garmin 上にマシンごとの重量・回数・セット実績が残っていないため、B日の評価は数値だけでなく主観重視で扱う
  - 次回以降のログで追加したい主観メモ:
    - 各主要マシンの最終setの RPE または RIR
    - どの部位に最も張りが入ったか
    - 翌日朝〜翌々日の軽い筋肉痛/張りの有無と部位
    - treadmill_main を処方どおり完遂できたか
    - warmup / cooldown が長くなった理由

## 2026-03-28（A60微修正）

- 種別: メニュー微修正
- 理由: 2026-03-28 の A_full とセカンドオピニオンで、A日は全体として成立している一方、Seated Leg Press と Abdominal の質に改善余地があると判断したため
- 変更前:
  - `Seated Leg Press` は `rest 30秒`
  - `Seated Leg Press` のrep品質基準は明文化していなかった
  - `Abdominal` は `下ろし3秒` のみ明記していた
- 変更後:
  - `Seated Leg Press` を `rest 45〜60秒` に変更
  - `Seated Leg Press` に `反動を使わない / 同じ深さまで下ろす / 上で抜き切らない / 脚そのもので止まる感覚を確認する` を追加
  - `Abdominal` に `腹を最後まで丸め切る / 股関節で逃げない / 最終2〜3repで腹が焼ける感覚を確認する` を追加
- 差分概要:
  - A日の後半トレッドミル18分は維持
  - A/Bの役割分担とGarminの扱いは維持
  - 数値の大きな変更ではなく、主力種目の質を優先する微修正のみ採用

## 2026-03-28

- 種別: 初期構築
- 理由: リポジトリ立ち上げにあたり、現時点の最新A60 / B60と設計思想を正本として固定するため
- 変更前: 管理対象ファイルなし
- 変更後:
  - `data/menus/current-menus.md` に現行A60 / B60を登録
  - `data/menus/design-philosophy.md` に現行の設計思想を登録
- 差分概要:
  - A日は「下半身刺激 + 有酸素主導日」
  - B日は「上半身刺激主導日 + 補助的有酸素」
  - 旧思想の「マシンから心拍をつないでトレッドミルへ接続する」は主設計から外す

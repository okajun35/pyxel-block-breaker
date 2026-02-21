# RIN Game 技術仕様書 v1.0

最終更新: 2026-02-21

## 1. 文書目的

- 現行実装に基づく技術仕様の明確化
- 実装・テスト・運用時の判断基準を統一
- 企画仕様との差分を減らし、保守性を高める

本書は `game/` 配下の実装を一次情報として作成する。

## 2. プロダクト概要（技術視点）

- 種別: Pyxel製リアルタイム2Dアクション（ブロック崩しベース）
- 表現ターゲット: `16ビット世代ゲーム機（スーパーファミコン相当）`
- 解像度: `240x180`（固定）
- フレーム進行: Pyxelの固定ステップ更新（60fps前提）
- 入出力:
  - キーボード入力（タイトル操作、プレイ操作、デバッグ系）
  - JSON保存（進行データ）
  - JSONL保存（ラン統計）
  - PNG保存（スクリーンショット）

## 3. 設計思想

## 3.1 実装方針

- 実用優先の軽量分割を採用
  - 複雑な抽象化より、責務ごとのモジュール分離を優先
- 表現制約を明示的に維持
  - 16ビット世代（スーパーファミコン相当）の視認性・演出密度を上限基準にする
- データ駆動を優先
  - 難易度・敵・アイテム・フェーズはCSV起点でロード
- 表示/入出力とロジックを分離
  - `App` はオーケストレーション
  - 計算ロジックは `systems.py` / `config.py` / 補助モジュールへ
- 1ランごとの完結性
  - ラン中状態とラン外成長を明確に分離

## 3.2 状態駆動UI

- 状態に応じて表示レイヤを切り替える
  - `TITLE`, `TUTORIAL`, `WAITING_START`, `PLAYING`, `STAGE_CLEAR`, `GAME_OVER`
- `build_layout()` で表示領域を一元管理し、座標の散逸を抑制
- セーフエリア（8px）を基準にHUD/パネルを配置

## 4. アーキテクチャ構成

## 4.1 起動経路

1. `block_breaker.py` から `App()` を生成
2. `App.__init__` で初期化（Pyxel, フォント, 音, 設定ロード, 各ストア/システム）
3. `pyxel.run(self.update, self.draw)` でゲームループ開始

## 4.2 モジュール責務

- `game/app.py`
  - ゲーム全体の状態遷移
  - 入力処理
  - 各システム呼び出し
  - 描画統合
- `game/systems.py`
  - `BallSystem`: ボール管理・速度正規化・増球
  - `EffectSystem`: アイテム効果レベル/タイマー/速度補正
  - `StageField`: ブロック配置・当たり判定・可動ブロック管理
- `game/config.py`
  - CSV読み込みと型付きプロファイル化
  - 難易度/プロトコル/フェーズ/敵/アイテムの参照API提供
- `game/progression.py`
  - ラン外進行（Core Shardと恒久強化）永続化
- `game/metrics.py`
  - ラン結果の追記保存（JSONL）
- `game/run_report.py`
  - 終了時レポートデータ整形
- `game/stage_design.py`
  - ステージ役割（Intro/Evasion/Rush/Control）定義
- `game/ui_layout.py`
  - 画面状態ごとのHUD/パネル配置情報生成
- `game/effects.py`
  - ヒットエフェクトの生成・寿命管理
- `game/assets.py` / `game/audio.py` / `game/automation.py`
  - 画像アセット、BGMパターン、自動実行設定

## 5. データ仕様

## 5.1 バランスデータ（CSV）

読み込み元:

- `docs/tables/difficulty_modes.csv`
- `docs/tables/protocol_profiles.csv`
- `docs/tables/run_phases.csv`
- `docs/tables/item_effects.csv`
- `docs/tables/enemy_scaling.csv`

設計ルール:

- バランス値はCSVを正とする
- コード側は `BalanceConfig` で型変換後に参照
- 実行時は enum キーで取得し、文字列分岐を局所化

## 5.2 永続化データ

- 進行保存: `tmp/progression.json`
  - `core_shards`
  - `life_upgrade_level`
  - `core_gain_upgrade_level`
  - `paddle_upgrade_level`
  - `tutorial_seen`
- ラン統計: `tmp/run_metrics.jsonl`
  - `mode`, `protocol`, `time_sec`, `score`, `max_combo`, `damage`, `phase`

## 6. ゲーム進行仕様（実装準拠）

## 6.1 ラン状態

- 初期遷移:
  - `TITLE` -> `TUTORIAL` or `PLAYING` -> `WAITING_START`/`PLAYING`
- 終端遷移:
  - `PLAYING` -> `STAGE_CLEAR` -> 次ステージ
  - `PLAYING` -> `GAME_OVER`

## 6.2 ステージ進行

- ステージ開始時に `StageField.setup()` を実行
- 要素:
  - 固定ブロック（通常/硬い）
  - 可動ブロック（HPあり）
  - アイテム内包ブロック
- 配置パターンはステージ番号で循環

## 6.3 敵とフェーズ

- 敵出現はフェーズ密度・ステージ役割で間隔調整
- Phase 5でボス `NULL_CORE_BOSS` をスポーン
- 敵性能は
  - 基本値（CSV）
  - 難易度補正
  - プロトコル補正
  - フェーズ経過補正
  を合成して決定

## 6.4 アイテム効果

- `W`: バー幅拡張（時間制）
- `S`: ボール減速（時間制）
- `M`: 増球（即時）
- `F`: ボール加速（時間制、ステージ2以降）
- 同アイテム再取得で
  - レベル増加（上限あり）
  - 効果時間延長

## 6.5 ダメージ/復活

- ダメージ原因:
  - ボール落下
  - 敵到達
- Story等では開始直後の被ダメ軽減を適用
- ライフ0時に難易度設定分の復活を適用

## 7. UI/描画仕様

## 7.1 描画ポリシー

- `PLAYING` 状態でゲーム世界を描画
- `TITLE/TUTORIAL/WAITING_START` はオーバーレイ優先
- HUDは状態で表示を抑制し、情報過密を避ける

## 7.2 解像度とレイアウト

- 画面サイズ: `240x180`
- セーフマージン: `8px`
- ブロックフィールドは中央寄せ
- HUDとプレイ領域の重なりを避けるため、上部/下部領域を固定化

## 7.3 日本語表示

- 優先フォント:
  - `assets/fonts/DotGothic16-Regular.ttf`
  - システム候補
  - `assets/fonts/PixelMplus12-Regular.ttf`
  - 最終フォールバック `assets/fonts/umplus_j12r.bdf`
- 実装メモ（2026-02-21更新）:
  - PyxelでBDFを使用する場合、`font_size` 指定は実質固定サイズ扱いになる。
  - そのため、ゲーム内HUD用には専用小フォント `assets/fonts/misaki_gothic.bdf` を優先し、本文向けとは分離して運用する。

## 8. 音・アセット仕様

- SEは `pyxel.sounds[]` を初期化して再生
- ステージBGMは `stage_music_pattern(stage)` で切替
- 画像アセットが揃う場合はスプライト描画を使用
- 不足時は図形描画にフォールバックし、プレイ継続性を優先

## 9. 自動化・運用

- 自動プレイ有効化:
  - `PYXEL_AUTORUN=1`
- 自動キャプチャ:
  - `PYXEL_AUTOCAP_FRAMES=30,90,150`
- 自動終了:
  - `PYXEL_AUTOEXIT_FRAME=240`
- スクリーンショット:
  - 手動 `C` キーで `tmp/jp.png` と履歴画像を保存

## 10. テスト方針

- テスト基盤: `unittest`
- 主対象:
  - CSV設定ロードと値整合
  - ステージ生成/アイテム出現条件
  - 効果時間延長ロジック
  - 進行保存・強化処理
  - メトリクス追記
  - アプリ初期化の主要補助メソッド

現状はロジック中心のテストが整備されており、描画結果の視覚回帰は自動キャプチャで補助する運用を採る。

## 11. 既知の技術的制約

- `App` に状態遷移・描画・進行制御が集中しており、規模拡大時の分割余地がある
- Pyxel依存部はヘッドレス実行制約があるため、完全自動E2Eには工夫が必要
- 一部ドキュメントに旧前提（旧解像度）が残る可能性があり、更新時は整合確認を要する

## 12. 将来拡張の推奨方針

- `App` の責務を段階的に分離
  - 入力制御
  - ラン進行usecase
  - 描画プレゼンテーション
- バランス改修はCSV先行で実施し、コード改修は参照層に限定
- UI変更は `ui_layout.py` を起点に行い、描画側の直値調整を避ける

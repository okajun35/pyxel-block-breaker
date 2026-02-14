# Block Breaker (Pyxel)

Pyxel で作ったブロックくずしゲームです。  
ステージ制、アイテム、ライフ、動くブロック、スクリーンショット保存に対応しています。

## 起動方法

```bash
cd /home/hddwm/rin_game
source .venv/bin/activate
python block_breaker.py
```

## 操作方法

- `1 / 2 / 3`: 難易度選択（開始前）
  - `1: Story`
  - `2: Standard`
  - `3: Hardcore`
- `TAB`: Protocol切替（開始前）
  - `Fusion` / `Reflex`
- `Story` は開始直後に被ダメ軽減あり
- `Fusion` は反射の補正が強め、`Reflex` は反射判定がシビアでスコア倍率高め
- `SPACE`: ゲーム開始（ステージ開始）
- `← / →`: バー移動
- `H`: HUD詳細表示のON/OFF
- `C`: スクリーンショット保存（`tmp/jp.png` と `tmp/shot_YYYYMMDD_HHMMSS.png`）
- `N`: ステージクリア後に次ステージへ進む
- `R`: 最初からリセット

## ルール

- ボールを落とすとライフが減ります（初期ライフ3）。
- 通常ブロックをすべて壊し、動くブロック（`MV`）も壊すとステージクリアです。
- `2` の表示があるブロックは 2 回当てると壊れます。
- ステージが進むと、硬いブロックとアイテム数が増えます。

## アイテム

- `W`: バーが長くなる
- `S`: ボールが遅くなる
- `M`: ボールが増える
- `F` (Stage 2+): ボールが速くなる

同じアイテムを連続で取ると効果レベルが上がり、効果時間も伸びます。

## 主要構成

- `block_breaker.py`: 起動エントリ
- `game/app.py`: ゲーム全体の制御（画面・入力・進行）
- `game/systems.py`: ボール/ステージ/効果システム
- `game/entities.py`: データ構造（Ball, FallingItem, MovingBlock）
- `game/enums.py`: 列挙型（ItemType, GameState）
- `game/constants.py`: 各種定数

## 開発者向け

責務の分け方（簡易図）:

```text
block_breaker.py
  -> App (game/app.py)
       -> BallSystem   (ボール生成・速度正規化・分裂)
       -> EffectSystem (アイテム効果レベル・効果時間・速度倍率)
       -> StageField   (ブロック配置・当たり判定・ステージ生成)
       -> entities     (Ball / FallingItem / MovingBlock)
       -> enums        (ItemType / GameState)
       -> constants    (ゲーム全体の定数)
```

拡張の目安:

- アイテム種類を増やす: `game/enums.py` と `game/systems.py` の `EffectSystem.apply_item`
- ステージ生成ルールを変える: `game/systems.py` の `StageField.setup/place_*`
- 画面表示を変える: `game/app.py` の `draw` 系
- 操作を増やす: `game/app.py` の `update`

## 自己確認（開発者）

- 日本語フォント描画の事前確認:
  - `python tools/self_check.py` を実行
  - `tmp/jp_selfcheck.png` で日本語表示を確認
- スクリーンショット確認:
  - ゲーム中に `C` キー
  - `tmp/jp.png`（固定名）と `tmp/shot_*.png`（履歴）が更新される
  - `python tools/self_check.py` でも `tmp/jp.png` を生成可能
- 起動時間の計測:
  - `python tools/measure_startup.py`

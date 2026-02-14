from datetime import datetime
from pathlib import Path
import time
import shutil
import os
import math
from typing import Iterable

import pyxel

from game.constants import (
    BALL_R,
    BASE_SPEED_RATE,
    BLOCK_COLS,
    BLOCK_GAP,
    BLOCK_H,
    BLOCK_OFFSET_X,
    BLOCK_OFFSET_Y,
    BLOCK_ROWS,
    BLOCK_W,
    HEIGHT,
    ITEM_FALL_SPEED,
    ITEM_SIZE,
    JP_FONT_FALLBACK_PATH,
    JP_FONT_PATH,
    JP_FONT_SYSTEM_CANDIDATES,
    JP_SMALL_FONT_PATH,
    JP_FONT_SIZE,
    START_PANEL_H,
    START_PANEL_W,
    START_PANEL_X,
    START_PANEL_Y,
    MOVING_BLOCK_H,
    MOVING_BLOCK_W,
    PADDLE_H,
    PADDLE_SPEED,
    PADDLE_Y,
    METRICS_PATH,
    PROGRESSION_PATH,
    ROOT_DIR,
    STAGE_CLEAR_WAIT,
    START_LIVES,
    TMP_DIR,
    WIDTH,
)
from game.config import BalanceConfig
from game.entities import Enemy, FallingItem
from game.enums import DifficultyMode, EnemyType, GameState, ItemType, ProtocolType
from game.systems import BallSystem, EffectSystem, StageField
from game.ui_layout import build_layout
from game.progression import ProgressionStore
from game.assets import AssetCatalog, EnemySpriteAnimator, SpriteSheet
from game.automation import AutoRunConfig
from game.effects import HitEffectSystem
from game.audio import stage_music_pattern
from game.run_report import build_run_report
from game.metrics import MetricsStore
from game.coaching import suggest_next_actions
from game.stage_design import stage_role


class App:
    def __init__(self):
        os.chdir(ROOT_DIR)
        self._startup_t0 = time.perf_counter()
        self._startup_logged = False
        pyxel.init(WIDTH, HEIGHT, title="Block Breaker")
        self.jp_font = self.load_jp_font(JP_FONT_SIZE)
        self.jp_small_font = self.load_jp_small_font()
        self.setup_audio()
        self.balance = BalanceConfig()
        self.auto = AutoRunConfig.from_env(os.environ)
        self.auto_captured_frames: set[int] = set()
        self.progression = ProgressionStore(PROGRESSION_PATH)
        self.metrics = MetricsStore(METRICS_PATH)
        self.asset_catalog = AssetCatalog()
        self.use_sprite_assets = False
        self.load_visual_assets()
        self.hit_fx = HitEffectSystem()
        self.ball_system = BallSystem()
        self.effect_system = EffectSystem(self.balance.item_effect_profiles)
        self.stage_field = StageField()
        self.reset()
        self.export_japanese_preview()
        pyxel.run(self.update, self.draw)

    def _font_candidates(self) -> Iterable[str]:
        env_font = os.getenv("JP_FONT_PATH")
        if env_font:
            yield env_font
        yield JP_FONT_PATH
        for path in JP_FONT_SYSTEM_CANDIDATES:
            yield path

    def load_jp_font(self, size: int):
        for path in self._font_candidates():
            try:
                return pyxel.Font(path, size)
            except Exception:
                continue
        try:
            return pyxel.Font(JP_FONT_FALLBACK_PATH)
        except Exception:
            return None

    def load_jp_small_font(self):
        try:
            return pyxel.Font(JP_SMALL_FONT_PATH)
        except Exception:
            return self.load_jp_font(JP_FONT_SIZE)

    def setup_audio(self):
        pyxel.sounds[0].set("c3e3g3c4", "p", "7", "n", 20)
        pyxel.sounds[1].set("g2b2d3g3", "p", "7", "n", 20)
        pyxel.sounds[2].set("f3c4", "p", "7", "n", 12)   # paddle
        pyxel.sounds[3].set("c3", "p", "6", "n", 8)      # block
        pyxel.sounds[4].set("g3c4e4", "p", "7", "n", 10) # item
        pyxel.sounds[5].set("c3b2a2", "p", "7", "f", 16) # miss life
        pyxel.sounds[6].set("c4g3e3c3", "p", "7", "f", 18)  # stage clear
        pyxel.sounds[7].set("a2f2d2c2", "p", "7", "f", 20)  # game over
        pyxel.sounds[8].set("e3g3b3e4", "t", "6", "n", 24)
        pyxel.sounds[9].set("d3a3d4", "t", "6", "n", 24)
        pyxel.sounds[10].set("c3f3a3", "s", "5", "n", 22)
        pyxel.sounds[11].set("g2c3d3", "s", "5", "n", 22)

    def load_visual_assets(self):
        if self.asset_catalog.missing_required_files():
            self.use_sprite_assets = False
            return
        try:
            pyxel.images[1].load(
                0, 0, str(self.asset_catalog.asset_path("sprites/sheet.png"))
            )
            pyxel.images[2].load(
                0, 0, str(self.asset_catalog.asset_path("ui/panel_start.png"))
            )
            self.use_sprite_assets = True
            self.load_stage_background(1)
        except Exception:
            self.use_sprite_assets = False

    def load_stage_background(self, stage: int):
        if not self.use_sprite_assets:
            return
        rel = self.asset_catalog.stage_background_relative(stage)
        pyxel.images[0].load(0, 0, str(self.asset_catalog.asset_path(rel)))

    def draw_text(self, x, y, text, col, jp=False, small_jp=False):
        if jp:
            font = self.jp_small_font if small_jp else self.jp_font
            if font is not None:
                pyxel.text(x, y, text, col, font)
                return
        pyxel.text(x, y, text, col)

    def capture_screen(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_name = f".screen_{datetime.now():%Y%m%d_%H%M%S_%f}.png"
        pyxel.screen.save(tmp_name, 1)
        shutil.move(tmp_name, path)

    def export_japanese_preview(self):
        tmp_dir = TMP_DIR
        tmp_dir.mkdir(parents=True, exist_ok=True)
        img = pyxel.Image(WIDTH, HEIGHT)
        img.cls(1)
        img.rect(START_PANEL_X, START_PANEL_Y, START_PANEL_W, START_PANEL_H, 0)
        img.rectb(START_PANEL_X, START_PANEL_Y, START_PANEL_W, START_PANEL_H, 7)
        if self.jp_font is not None:
            img.text(START_PANEL_X + 10, START_PANEL_Y + 8, "あそびかた", 10, self.jp_font)
        if self.jp_small_font is not None:
            x = START_PANEL_X + 10
            y = START_PANEL_Y + 20
            img.text(x, y, "1/2/3: むずかしさ", 7, self.jp_small_font)
            img.text(x, y + 12, "TAB: モードきりかえ", 7, self.jp_small_font)
            img.text(x, y + 24, "ひだり/みぎ: いどう", 7, self.jp_small_font)
            img.text(x, y + 36, "W/S/M/F: アイテム", 7, self.jp_small_font)
            img.text(x, y + 48, "SPACE: スタート", 10, self.jp_small_font)
            img.text(x, y + 60, "C: 保存  U:ライフ強化", 10, self.jp_small_font)
        img.save(str(tmp_dir / "jp_preview.png"), 1)

    def reset(self):
        self.paddle_w = 24
        self.paddle_x = WIDTH // 2 - self.paddle_w // 2
        self.ball_speed_rate = BASE_SPEED_RATE
        if not hasattr(self, "selected_mode"):
            self.selected_mode = DifficultyMode.STANDARD
        if not hasattr(self, "selected_protocol"):
            self.selected_protocol = ProtocolType.FUSION
        self.run_elapsed_frames = 0
        self.current_phase = self.balance.get_phase_by_elapsed_sec(0)
        difficulty = self.balance.get_difficulty(self.selected_mode)
        self.remaining_revives = difficulty.revive_count
        base_lives = difficulty.base_lives
        base_lives += self._life_upgrade_level()
        self.lives = base_lives
        self.stage = 1
        self.run_rewarded = False
        self.run_metric_recorded = False
        self.damage_taken_total = 0
        self.recent_damage_causes: list[str] = []
        self.danger_flash_timer = 0
        self.max_combo = 0
        self.last_report = None
        self.next_tips: list[str] = []
        self.blocks_broken_total = 0
        self.items_collected_total = 0
        self.intro_spawn_index = 0
        self.state = GameState.WAITING_START
        self.stage_clear_timer = 0
        self.shot_message = ""
        self.shot_message_timer = 0
        self.items: list[FallingItem] = []
        self.enemies: list[Enemy] = []
        self.enemy_spawn_timer = 0
        self.phase_boss_spawned = False
        self.score = 0
        self.combo = 0
        self.combo_timer = 0
        self.hud_detailed = False
        self.title_menu_index = 0
        self.effect_system.reset_all()
        self.setup_stage()
        self.state = GameState.TITLE

    def setup_stage(self):
        self.stage_role = stage_role(self.stage)
        difficulty = self.balance.get_difficulty(self.selected_mode)
        protocol = self.balance.get_protocol(self.selected_protocol)
        elapsed_sec = self.run_elapsed_frames // 60
        self.current_phase = self.balance.get_phase_by_elapsed_sec(elapsed_sec)
        self.enemies = []
        self.enemy_spawn_timer = 0
        self.phase_boss_spawned = False
        self.stage_field.setup(
            self.stage,
            enemy_hp_mul=difficulty.enemy_hp_mul * protocol.enemy_hp_mul,
            item_spawn_mul=difficulty.drop_rate_mul * protocol.item_spawn_mul,
            phase_density_mul=self.current_phase.enemy_density_mul * self.stage_role.enemy_spawn_rate_mul,
            phase_reward_mul=self.current_phase.event_weight_reward + 0.7,
            moving_speed_mul=self.stage_role.moving_speed_mul,
            preferred_item=self.stage_role.preferred_item,
        )
        if self.stage == 1:
            self.stage_field.item_blocks[0][BLOCK_COLS // 2] = ItemType.WIDE
        self.load_stage_background(self.stage)
        self.respawn_ball()

    def respawn_ball(self):
        self.ball_system.respawn_ball(WIDTH // 2, HEIGHT // 2)
        self.effect_system.on_respawn()
        self.items = []
        self.state = GameState.WAITING_START

    def _spawn_interval_frames(self) -> int:
        density = max(0.2, self.current_phase.enemy_density_mul * self.stage_role.enemy_spawn_rate_mul)
        base = int(90 / density)
        return max(15, base)

    def _is_intro_fixed(self) -> bool:
        return self.stage == 1 and self.run_elapsed_frames < 60 * 5

    def _spawn_enemy(self):
        elapsed_sec = self.run_elapsed_frames // 60
        self.current_phase = self.balance.get_phase_by_elapsed_sec(elapsed_sec)
        if self._is_intro_fixed():
            sequence = [
                EnemyType.DRONE,
                EnemyType.DRONE,
                EnemyType.SPLITTER,
                EnemyType.DRONE,
                EnemyType.SNIPER_ORB,
                EnemyType.SHIELD_NODE,
            ]
            enemy_type = sequence[self.intro_spawn_index % len(sequence)]
            self.intro_spawn_index += 1
        else:
            r = pyxel.rndi(0, 99)
            if r < 55:
                enemy_type = EnemyType.DRONE
            elif r < 75:
                enemy_type = EnemyType.SPLITTER
            elif r < 92:
                enemy_type = EnemyType.SNIPER_ORB
            else:
                enemy_type = EnemyType.SHIELD_NODE

        profile = self.balance.enemy_profiles[enemy_type]
        difficulty = self.balance.get_difficulty(self.selected_mode)
        protocol = self.balance.get_protocol(self.selected_protocol)
        phase_index = max(0, self.current_phase.phase_id - 1)

        hp_mul = (1.0 + phase_index * (profile.phase_hp_gain_pct / 100.0))
        speed_mul = (1.0 + phase_index * (profile.phase_speed_gain_pct / 100.0))
        hp = profile.base_hp * hp_mul * difficulty.enemy_hp_mul * protocol.enemy_hp_mul
        speed = profile.base_speed * speed_mul
        if self.selected_mode == DifficultyMode.HARDCORE:
            hp *= 1.0 + (profile.hard_mode_extra_hp_pct / 100.0)
            speed *= 1.0 + (profile.hard_mode_extra_speed_pct / 100.0)

        if self._is_intro_fixed():
            fixed_x = [28, 52, 76, 100, 124, 148, 172, 196]
            x = fixed_x[self.intro_spawn_index % len(fixed_x)]
            vx = 0.22 if self.intro_spawn_index % 2 == 0 else -0.22
        else:
            x = pyxel.rndi(10, WIDTH - 10)
            vx = pyxel.rndf(-0.4, 0.4)
        vy = 0.15 + speed * 0.08
        self.enemies.append(
            Enemy(
                type=enemy_type,
                x=x,
                y=18,
                vx=vx,
                vy=vy,
                hp=hp,
                damage=profile.collision_damage,
            )
        )

    def _spawn_phase_boss(self):
        if self.phase_boss_spawned:
            return
        if self.current_phase.phase_id < 5:
            return
        profile = self.balance.enemy_profiles[EnemyType.NULL_CORE_BOSS]
        difficulty = self.balance.get_difficulty(self.selected_mode)
        protocol = self.balance.get_protocol(self.selected_protocol)
        hp = profile.base_hp * difficulty.enemy_hp_mul * protocol.enemy_hp_mul
        self.enemies.append(
            Enemy(
                type=EnemyType.NULL_CORE_BOSS,
                x=WIDTH // 2,
                y=22,
                vx=0.7,
                vy=0.03,
                hp=hp,
                damage=profile.collision_damage,
            )
        )
        self.phase_boss_spawned = True

    def _enemy_score(self, enemy_type: EnemyType) -> int:
        base = {
            EnemyType.DRONE: 30,
            EnemyType.SPLITTER: 45,
            EnemyType.SNIPER_ORB: 55,
            EnemyType.SHIELD_NODE: 70,
            EnemyType.NULL_CORE_BOSS: 300,
        }[enemy_type]
        difficulty = self.balance.get_difficulty(self.selected_mode)
        protocol = self.balance.get_protocol(self.selected_protocol)
        combo_mul = 1.0 + min(self.combo, 20) * 0.05 * protocol.combo_score_mul
        return int(base * difficulty.score_mul * protocol.base_score_mul * combo_mul)

    def _record_damage_cause(self, cause: str):
        self.recent_damage_causes.append(cause)
        if len(self.recent_damage_causes) > 6:
            self.recent_damage_causes.pop(0)

    def _apply_enemy_damage(self, damage: int, cause: str):
        difficulty = self.balance.get_difficulty(self.selected_mode)
        actual = max(1, math.ceil(damage * difficulty.enemy_damage_mul))
        elapsed_sec = self.run_elapsed_frames // 60
        if elapsed_sec < difficulty.early_guard_seconds:
            actual = max(1, math.ceil(actual * 0.5))
        self.lives -= actual
        self.damage_taken_total += actual
        self._record_damage_cause(cause)
        if self.lives <= 0:
            if self.remaining_revives > 0:
                self.remaining_revives -= 1
                self.lives = 1
            else:
                self.state = GameState.GAME_OVER
                self.play_se(7)
                self._grant_core_for_run_end()

    def update_enemies(self):
        elapsed_sec = self.run_elapsed_frames // 60
        self.current_phase = self.balance.get_phase_by_elapsed_sec(elapsed_sec)
        self._spawn_phase_boss()
        self.enemy_spawn_timer -= 1
        if self.enemy_spawn_timer <= 0:
            self._spawn_enemy()
            self.enemy_spawn_timer = self._spawn_interval_frames()

        alive = []
        for enemy in self.enemies:
            enemy.x += enemy.vx
            enemy.y += enemy.vy
            if enemy.x < 4 or enemy.x > WIDTH - 4:
                enemy.vx *= -1
            if enemy.y >= PADDLE_Y:
                self._apply_enemy_damage(enemy.damage, f"enemy_reach:{enemy.type.value}")
                if self.state == GameState.GAME_OVER:
                    return
                self.play_se(5)
                continue
            if enemy.y >= PADDLE_Y - 22:
                self.danger_flash_timer = 8
            alive.append(enemy)
        self.enemies = alive

    def resolve_ball_enemy_collisions(self):
        for ball in self.ball_system.balls:
            for enemy in self.enemies:
                dx = ball.x - enemy.x
                dy = ball.y - enemy.y
                if dx * dx + dy * dy > 25:
                    continue
                enemy.hp -= 25
                ball.vy *= -1
                self.hit_fx.spawn_block_hit(enemy.x, enemy.y)
                if enemy.hp <= 0:
                    self.score += self._enemy_score(enemy.type)
                    self.combo += 1
                    self.max_combo = max(self.max_combo, self.combo)
                    self.combo_timer = 180
                    is_boss = enemy.type == EnemyType.NULL_CORE_BOSS
                    self.hit_fx.spawn_enemy_hit(enemy.x, enemy.y, boss=is_boss)
                    if is_boss:
                        self.hit_fx.spawn_boss_burst(enemy.x, enemy.y)
                    self.play_se(3)
        self.enemies = [e for e in self.enemies if e.hp > 0]

    def next_stage(self):
        self._grant_core_for_stage_clear()
        self.stage += 1
        self.stage_clear_timer = 0
        self.effect_system.reset_stage_effects()
        self.setup_stage()
        self.play_stage_music()

    def _life_upgrade_level(self) -> int:
        if not hasattr(self, "progression"):
            return 0
        return self.progression.state.life_upgrade_level

    def _paddle_upgrade_bonus(self) -> int:
        if not hasattr(self, "progression"):
            return 0
        return self.progression.state.paddle_upgrade_level * 4

    def _core_gain_multiplier(self) -> float:
        if not hasattr(self, "progression"):
            return 1.0
        return 1.0 + self.progression.state.core_gain_upgrade_level * 0.2

    def _grant_core_for_stage_clear(self):
        if not hasattr(self, "progression"):
            return
        gained = 3 + min(3, self.stage)
        self.progression.add_core(int(gained * self._core_gain_multiplier()))

    def _grant_core_for_run_end(self):
        if not hasattr(self, "progression"):
            return
        if self.run_rewarded:
            return
        gained = max(1, self.score // 200)
        self.progression.add_core(int(gained * self._core_gain_multiplier()))
        self.run_rewarded = True

    def _build_report(self):
        self.last_report = build_run_report(
            elapsed_frames=self.run_elapsed_frames,
            max_combo=self.max_combo,
            damage_taken=self.damage_taken_total,
            cleared_phase=self.current_phase.phase_id,
            score=self.score,
        )
        self.next_tips = suggest_next_actions(self.last_report, self.recent_damage_causes)

    def _record_run_metric(self):
        if self.run_metric_recorded:
            return
        if self.last_report is None:
            self._build_report()
        self.metrics.append(
            mode=self.selected_mode.value,
            protocol=self.selected_protocol.value,
            time_sec=self.last_report.time_sec,
            score=self.last_report.score,
            max_combo=self.last_report.max_combo,
            damage=self.last_report.damage_taken,
            phase=self.last_report.cleared_phase,
        )
        self.run_metric_recorded = True

    def play_stage_music(self):
        pyxel.stop(2)
        pyxel.play(2, stage_music_pattern(self.stage))

    def play_se(self, sound_id: int):
        pyxel.play(3, sound_id)

    def save_screen_shot(self):
        tmp_dir = TMP_DIR
        tmp_dir.mkdir(parents=True, exist_ok=True)
        target_fixed = tmp_dir / "jp.png"
        target_latest = tmp_dir / f"shot_{datetime.now():%Y%m%d_%H%M%S}.png"
        try:
            self.capture_screen(target_fixed)
            self.capture_screen(target_latest)
        except Exception:
            self.shot_message = "save failed"
            self.shot_message_timer = 120
            return
        self.shot_message = f"saved: {target_fixed.as_posix()}"
        self.shot_message_timer = 180

    def auto_capture(self):
        if not self.auto.enabled:
            return
        if pyxel.frame_count not in self.auto.capture_frames:
            return
        if pyxel.frame_count in self.auto_captured_frames:
            return
        self.auto_captured_frames.add(pyxel.frame_count)
        tmp_dir = TMP_DIR
        tmp_dir.mkdir(parents=True, exist_ok=True)
        path = tmp_dir / f"auto_{pyxel.frame_count:04d}.png"
        try:
            self.capture_screen(path)
        except Exception:
            return

    def auto_play(self):
        if not self.auto.enabled:
            return
        if self.state in (GameState.TITLE, GameState.WAITING_START) and pyxel.frame_count > 10:
            self.state = GameState.PLAYING
        if self.state == GameState.PLAYING and self.ball_system.balls:
            target_x = self.ball_system.balls[0].x
            paddle_center = self.paddle_x + self.paddle_w / 2
            if target_x < paddle_center - 1:
                self.paddle_x -= PADDLE_SPEED
            elif target_x > paddle_center + 1:
                self.paddle_x += PADDLE_SPEED
            self.paddle_x = max(0, min(WIDTH - self.paddle_w, self.paddle_x))
        self.auto_capture()
        if self.auto.exit_frame > 0 and pyxel.frame_count >= self.auto.exit_frame:
            self._build_report()
            self._record_run_metric()
            os._exit(0)

    def update(self):
        if pyxel.btnp(pyxel.KEY_R):
            self.reset()
            return
        if pyxel.btnp(pyxel.KEY_H):
            self.hud_detailed = not self.hud_detailed
        if pyxel.btnp(pyxel.KEY_C):
            self.save_screen_shot()
        if self.shot_message_timer > 0:
            self.shot_message_timer -= 1
        self.auto_play()

        if self.state == GameState.GAME_OVER:
            self._grant_core_for_run_end()
            if self.last_report is None:
                self._build_report()
            self._record_run_metric()
            return

        if self.state == GameState.STAGE_CLEAR:
            self.stage_clear_timer -= 1
            if self.stage_clear_timer <= 0 or pyxel.btnp(pyxel.KEY_N):
                self.next_stage()
            return

        if self.state == GameState.TITLE:
            if pyxel.btnp(pyxel.KEY_UP):
                self.title_menu_index = (self.title_menu_index - 1) % 3
            if pyxel.btnp(pyxel.KEY_DOWN):
                self.title_menu_index = (self.title_menu_index + 1) % 3
            if pyxel.btnp(pyxel.KEY_1):
                self.selected_mode = DifficultyMode.STORY
                self.setup_stage()
            if pyxel.btnp(pyxel.KEY_2):
                self.selected_mode = DifficultyMode.STANDARD
                self.setup_stage()
            if pyxel.btnp(pyxel.KEY_3):
                self.selected_mode = DifficultyMode.HARDCORE
                self.setup_stage()
            if pyxel.btnp(pyxel.KEY_TAB):
                self.selected_protocol = (
                    ProtocolType.REFLEX
                    if self.selected_protocol == ProtocolType.FUSION
                    else ProtocolType.FUSION
                )
                self.setup_stage()
            if pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_RIGHT):
                if self.title_menu_index == 1:
                    if self.selected_mode == DifficultyMode.STORY:
                        self.selected_mode = DifficultyMode.STANDARD
                    elif self.selected_mode == DifficultyMode.STANDARD:
                        self.selected_mode = DifficultyMode.HARDCORE
                    else:
                        self.selected_mode = DifficultyMode.STORY
                    self.setup_stage()
                if self.title_menu_index == 2:
                    self.selected_protocol = (
                        ProtocolType.REFLEX
                        if self.selected_protocol == ProtocolType.FUSION
                        else ProtocolType.FUSION
                    )
                    self.setup_stage()
            if pyxel.btnp(pyxel.KEY_U) and hasattr(self, "progression"):
                upgraded = self.progression.try_upgrade_life()
                self.shot_message = "upgrade life +1" if upgraded else "need 10 core"
                self.shot_message_timer = 120
            if pyxel.btnp(pyxel.KEY_I) and hasattr(self, "progression"):
                upgraded = self.progression.try_upgrade_core_gain()
                self.shot_message = "core gain +20%" if upgraded else "need 12 core"
                self.shot_message_timer = 120
            if pyxel.btnp(pyxel.KEY_O) and hasattr(self, "progression"):
                upgraded = self.progression.try_upgrade_paddle()
                self.shot_message = "base paddle +4" if upgraded else "need 10 core"
                self.shot_message_timer = 120
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE):
                self.state = GameState.PLAYING
            return

        if self.state == GameState.WAITING_START:
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.state = GameState.PLAYING
            return

        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0

        if pyxel.btn(pyxel.KEY_LEFT):
            self.paddle_x -= PADDLE_SPEED
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.paddle_x += PADDLE_SPEED
        self.paddle_x = max(0, min(WIDTH - self.paddle_w, self.paddle_x))
        protocol = self.balance.get_protocol(self.selected_protocol)
        reflect_margin_px = max(0, protocol.reflect_window_ms // 20)

        alive_balls = []
        self.run_elapsed_frames += 1
        for ball in self.ball_system.balls:
            ball.x += ball.vx * self.ball_speed_rate
            ball.y += ball.vy * self.ball_speed_rate

            if ball.x <= BALL_R or ball.x >= WIDTH - BALL_R:
                ball.vx *= -1
            if ball.y <= BALL_R:
                ball.vy *= -1
            if ball.y >= HEIGHT + BALL_R:
                continue

            if (
                ball.vy > 0
                and PADDLE_Y - reflect_margin_px
                <= ball.y + BALL_R
                <= PADDLE_Y + PADDLE_H + reflect_margin_px
                and self.paddle_x <= ball.x <= self.paddle_x + self.paddle_w
            ):
                assist = 1.0 + (protocol.paddle_aim_assist_deg / 40.0)
                offset = (
                    (ball.x - (self.paddle_x + self.paddle_w / 2)) / (self.paddle_w / 2)
                ) / assist
                ball.vx, ball.vy = self.ball_system.normalized_velocity(offset, -1.3)
                self.play_se(2)

            hit_block, spawned_item, destroyed = self.stage_field.collide_ball(ball)
            if hit_block:
                self.play_se(3)
                self.hit_fx.spawn_block_hit(ball.x, ball.y)
            if spawned_item:
                self.items.append(spawned_item)
            if destroyed:
                self.blocks_broken_total += 1

            alive_balls.append(ball)

        self.ball_system.balls = alive_balls
        if not self.ball_system.balls:
            self.lives -= 1
            self._record_damage_cause("ball_drop")
            if self.lives <= 0:
                if self.remaining_revives > 0:
                    self.remaining_revives -= 1
                    self.lives = 1
                else:
                    self.state = GameState.GAME_OVER
                    self.play_se(7)
                    self._grant_core_for_run_end()
                    self._build_report()
                    self._record_run_metric()
                    return
            self.play_se(5)
            self.respawn_ball()
            return

        self.stage_field.update_moving_block()
        self.update_enemies()
        if self.state == GameState.GAME_OVER:
            self._grant_core_for_run_end()
            if self.last_report is None:
                self._build_report()
            self._record_run_metric()
            return
        self.resolve_ball_enemy_collisions()
        if self.stage_field.all_cleared():
            self.state = GameState.STAGE_CLEAR
            self.stage_clear_timer = STAGE_CLEAR_WAIT
            self.play_se(6)
            return

        self.update_items()
        self.paddle_w, self.ball_speed_rate = self.effect_system.tick()
        self.paddle_w += self._paddle_upgrade_bonus()
        self.paddle_x = max(0, min(WIDTH - self.paddle_w, self.paddle_x))
        self.hit_fx.tick()

    def update_items(self):
        alive_items = []
        for item in self.items:
            item.y += ITEM_FALL_SPEED
            if (
                PADDLE_Y <= item.y <= PADDLE_Y + PADDLE_H
                and self.paddle_x <= item.x <= self.paddle_x + self.paddle_w
            ):
                self.effect_system.apply_item(item.type, self.ball_system)
                self.items_collected_total += 1
                self.play_se(4)
                continue
            if item.y > HEIGHT + ITEM_SIZE:
                continue
            alive_items.append(item)
        self.items = alive_items

    def draw(self):
        layout = build_layout(self.state)
        if not self._startup_logged:
            elapsed = time.perf_counter() - self._startup_t0
            tmp_dir = TMP_DIR
            tmp_dir.mkdir(parents=True, exist_ok=True)
            (tmp_dir / "startup_trace.txt").write_text(
                f"first_draw_elapsed={elapsed:.4f}s\n"
                f"jp_font_loaded={self.jp_font is not None}\n"
                f"jp_small_font_loaded={self.jp_small_font is not None}\n",
                encoding="utf-8",
            )
            self._startup_logged = True

        pyxel.cls(1)
        if self.use_sprite_assets:
            pyxel.blt(0, 0, 0, 0, 0, WIDTH, HEIGHT)
        if layout.show_hud:
            self.draw_text(4, layout.top_text_y, "LR Move  H HUD  C Shot", 7)
            if self.hud_detailed:
                self.draw_text(4, layout.top_sub_y, f"{self.selected_mode.value}/{self.selected_protocol.value}", 12)
                self.draw_text(WIDTH - 74, layout.top_sub_y, self.current_phase.label[:8], 12)

        draw_world = self.state not in (GameState.WAITING_START, GameState.TITLE)
        if draw_world:
            for row in range(BLOCK_ROWS):
                for col in range(BLOCK_COLS):
                    if self.stage_field.block_hp[row][col]:
                        bx = BLOCK_OFFSET_X + col * (BLOCK_W + BLOCK_GAP)
                        by = BLOCK_OFFSET_Y + row * (BLOCK_H + BLOCK_GAP)
                        block_color = 2 if self.stage_field.block_hp[row][col] == 2 else 8 + row
                        if self.use_sprite_assets:
                            sprite = SpriteSheet.BLOCK_HARD if self.stage_field.block_hp[row][col] == 2 else SpriteSheet.BLOCK_NORMAL
                            pyxel.blt(bx, by, 1, sprite.u, sprite.v, sprite.w, sprite.h, 1)
                        else:
                            pyxel.rect(bx, by, BLOCK_W, BLOCK_H, block_color)
                        if self.stage_field.block_hp[row][col] == 2:
                            self.draw_text(bx + 1, by + 1, "2", 7)
                        item_type = self.stage_field.item_blocks[row][col]
                        if item_type == ItemType.WIDE:
                            self.draw_text(bx + 9, by + 1, "W", 9)
                        if item_type == ItemType.SLOW:
                            self.draw_text(bx + 9, by + 1, "S", 11)
                        if item_type == ItemType.MULTI:
                            self.draw_text(bx + 9, by + 1, "M", 14)
                        if item_type == ItemType.FAST:
                            self.draw_text(bx + 9, by + 1, "F", 8)

            moving = self.stage_field.moving_block
            if moving.hp > 0:
                if self.use_sprite_assets:
                    s = SpriteSheet.MOVING_BLOCK
                    pyxel.blt(int(moving.x), int(moving.y), 1, s.u, s.v, s.w, s.h, 1)
                else:
                    pyxel.rect(moving.x, moving.y, MOVING_BLOCK_W, MOVING_BLOCK_H, 3)
                self.draw_text(moving.x + 6, moving.y + 1, "MV", 7)
                if moving.hp == 2:
                    self.draw_text(moving.x + 1, moving.y + 1, "2", 7)

            for item in self.items:
                color = 9
                if item.type == ItemType.SLOW:
                    color = 11
                if item.type == ItemType.MULTI:
                    color = 14
                if item.type == ItemType.FAST:
                    color = 8
                if self.use_sprite_assets:
                    s = SpriteSheet.ITEM_W
                    if item.type == ItemType.SLOW:
                        s = SpriteSheet.ITEM_S
                    if item.type == ItemType.MULTI:
                        s = SpriteSheet.ITEM_M
                    if item.type == ItemType.FAST:
                        s = SpriteSheet.ITEM_F
                    pyxel.blt(int(item.x - s.w // 2), int(item.y - s.h // 2), 1, s.u, s.v, s.w, s.h, 1)
                else:
                    pyxel.rect(item.x - ITEM_SIZE // 2, item.y - ITEM_SIZE // 2, ITEM_SIZE, ITEM_SIZE, color)

            for enemy in self.enemies:
                color = 8
                if enemy.type == EnemyType.SPLITTER:
                    color = 14
                if enemy.type == EnemyType.SNIPER_ORB:
                    color = 11
                if enemy.type == EnemyType.SHIELD_NODE:
                    color = 2
                if enemy.type == EnemyType.NULL_CORE_BOSS:
                    color = 7
                if self.use_sprite_assets:
                    s = EnemySpriteAnimator.frame_for(enemy.type, pyxel.frame_count)
                    pyxel.blt(int(enemy.x - s.w // 2), int(enemy.y - s.h // 2), 1, s.u, s.v, s.w, s.h, 1)
                else:
                    radius = 3 if enemy.type != EnemyType.NULL_CORE_BOSS else 6
                    pyxel.circ(enemy.x, enemy.y, radius, color)

            pyxel.rect(self.paddle_x, PADDLE_Y, self.paddle_w, PADDLE_H, 10)
            for ball in self.ball_system.balls:
                pyxel.circ(ball.x, ball.y, BALL_R, 7)
            for fx in self.hit_fx.effects:
                pyxel.pset(int(fx.x), int(fx.y), fx.color)
            if self.danger_flash_timer > 0:
                pyxel.rect(0, PADDLE_Y - 2, WIDTH, 1, 8)
                self.danger_flash_timer -= 1
            if self._is_intro_fixed():
                if self.blocks_broken_total < 5:
                    self.draw_text(4, 30, "Goal1: break 5 blocks", 10)
                elif self.items_collected_total < 1:
                    self.draw_text(4, 30, "Goal2: get 1 item", 10)
                else:
                    self.draw_text(4, 30, "Goal3: clear stage 1", 10)

        if layout.show_hud:
            self.draw_text(4, layout.upper_bottom_y, f"Score:{self.score}", 10)
            if self.combo > 0 or self.hud_detailed:
                self.draw_text(90, layout.upper_bottom_y, f"Combo:{self.combo}", 6)
            self.draw_text(4, layout.bottom_y, f"Balls:{len(self.ball_system.balls)}", 7)
            self.draw_text(74, layout.bottom_y, f"Life:{self.lives}", 8)
            self.draw_text(124, layout.bottom_y, f"Rv:{self.remaining_revives}", 14)
            self.draw_text(WIDTH - 110, layout.bottom_y, self.stage_role.label, 12)
            self.draw_text(WIDTH - 54, layout.bottom_y, f"Stg:{self.stage}", 10)
            if self.hud_detailed:
                self.draw_text(
                    4,
                    layout.bottom_y - 12,
                    f"Hard:{self.stage_field.hard_count} Item:{self.stage_field.item_count}",
                    5,
                )

                if self.effect_system.effect_wide_timer > 0:
                    self.draw_text(
                        140,
                        layout.upper_bottom_y,
                        f"W{self.effect_system.effect_wide_level}:{self.effect_system.effect_wide_timer // 60}s",
                        9,
                    )
                if self.effect_system.effect_slow_timer > 0:
                    self.draw_text(
                        178,
                        layout.upper_bottom_y,
                        f"S{self.effect_system.effect_slow_level}:{self.effect_system.effect_slow_timer // 60}s",
                        11,
                    )
                if self.effect_system.effect_fast_timer > 0:
                    self.draw_text(
                        216,
                        layout.upper_bottom_y,
                        f"F{self.effect_system.effect_fast_level}:{self.effect_system.effect_fast_timer // 60}s",
                        8,
                    )
        if self.shot_message_timer > 0:
            self.draw_text(4, layout.toast_y, self.shot_message, 10)

        if self.state == GameState.STAGE_CLEAR:
            self.draw_text(43, 56, f"STAGE {self.stage} CLEAR!", 11)
            self.draw_text(28, 66, "Next: N or auto", 7)
        if self.state == GameState.TITLE:
            if self.use_sprite_assets:
                pyxel.blt(layout.panel_x, layout.panel_y, 2, 0, 0, layout.panel_w, layout.panel_h, 1)
            else:
                pyxel.rect(layout.panel_x, layout.panel_y, layout.panel_w, layout.panel_h, 0)
                pyxel.rectb(layout.panel_x, layout.panel_y, layout.panel_w, layout.panel_h, 7)
            x = layout.panel_x + 10
            y = layout.panel_y + 8
            self.draw_text(x, y, "PIT ARK BREAKER", 10)
            cursor = [">", " ", " "]
            cursor[self.title_menu_index] = ">"
            self.draw_text(x, y + 14, f"{cursor[0]} Start", 7)
            self.draw_text(x, y + 26, f"{cursor[1]} Difficulty: {self.selected_mode.value}", 7)
            self.draw_text(x, y + 38, f"{cursor[2]} Protocol: {self.selected_protocol.value}", 7)
            self.draw_text(x, y + 54, "UP/DOWN: select", 12)
            self.draw_text(x, y + 64, "LEFT/RIGHT: change", 12)
            self.draw_text(x, y + 74, "ENTER/SPACE: start", 10)
            self.draw_text(x, y + 88, "U/I/O: upgrades", 11)
            if hasattr(self, "progression"):
                core = self.progression.state.core_shards
                self.draw_text(x, y + 100, f"Core:{core}", 7)
        if self.state == GameState.WAITING_START:
            if self.use_sprite_assets:
                pyxel.blt(layout.panel_x, layout.panel_y, 2, 0, 0, layout.panel_w, layout.panel_h, 1)
            else:
                pyxel.rect(layout.panel_x, layout.panel_y, layout.panel_w, layout.panel_h, 0)
                pyxel.rectb(layout.panel_x, layout.panel_y, layout.panel_w, layout.panel_h, 7)
            x = layout.panel_x + 10
            y = layout.panel_y + 8
            self.draw_text(x, y, "READY", 10)
            self.draw_text(x, y + 16, "SPACE: continue", 7)
            self.draw_text(x, y + 28, "LEFT/RIGHT: move", 7)
            self.draw_text(x, y + 40, "C: screenshot", 7)
        if self.state == GameState.GAME_OVER:
            self.draw_text(51, 58, "GAME OVER", 8)
            self.draw_text(43, 68, "Press R to retry", 7)
            if self.last_report is not None:
                self.draw_text(36, 80, f"Time:{self.last_report.time_sec}s", 7)
                self.draw_text(36, 90, f"MaxCombo:{self.last_report.max_combo}", 7)
                self.draw_text(36, 100, f"Damage:{self.last_report.damage_taken}", 7)
                self.draw_text(36, 110, f"Phase:{self.last_report.cleared_phase}", 7)
            for i, tip in enumerate(self.next_tips[:2]):
                self.draw_text(126, 92 + i * 10, tip[:14], 12, jp=True, small_jp=True)

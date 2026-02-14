from datetime import datetime
from pathlib import Path
import time
import shutil
import os
import math

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
    JP_SMALL_FONT_PATH,
    JP_FONT_SIZE,
    MOVING_BLOCK_H,
    MOVING_BLOCK_W,
    PADDLE_H,
    PADDLE_SPEED,
    PADDLE_Y,
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
        self.ball_system = BallSystem()
        self.effect_system = EffectSystem(self.balance.item_effect_profiles)
        self.stage_field = StageField()
        self.reset()
        self.export_japanese_preview()
        pyxel.run(self.update, self.draw)

    def load_jp_font(self, size: int):
        try:
            return pyxel.Font(JP_FONT_PATH, size)
        except Exception:
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
        img.rect(8, 28, 144, 72, 0)
        img.rectb(8, 28, 144, 72, 7)
        if self.jp_font is not None:
            img.text(14, 36, "あそびかた", 10, self.jp_font)
        if self.jp_small_font is not None:
            img.text(14, 48, "ひだり/みぎ いどう", 7, self.jp_small_font)
            img.text(14, 58, "ぜんぶこわして クリア", 7, self.jp_small_font)
            img.text(14, 68, "W:バー  S:スロー", 7, self.jp_small_font)
            img.text(14, 78, "M:+たま  F:はやい(2~)", 7, self.jp_small_font)
            img.text(14, 90, "SPACE:スタート C:保存", 10, self.jp_small_font)
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
        self.lives = difficulty.base_lives
        self.stage = 1
        self.state = GameState.WAITING_START
        self.stage_clear_timer = 0
        self.shot_message = ""
        self.shot_message_timer = 0
        self.items: list[FallingItem] = []
        self.enemies: list[Enemy] = []
        self.enemy_spawn_timer = 0
        self.score = 0
        self.combo = 0
        self.combo_timer = 0
        self.effect_system.reset_all()
        self.setup_stage()

    def setup_stage(self):
        difficulty = self.balance.get_difficulty(self.selected_mode)
        protocol = self.balance.get_protocol(self.selected_protocol)
        elapsed_sec = self.run_elapsed_frames // 60
        self.current_phase = self.balance.get_phase_by_elapsed_sec(elapsed_sec)
        self.enemies = []
        self.enemy_spawn_timer = 0
        self.stage_field.setup(
            self.stage,
            enemy_hp_mul=difficulty.enemy_hp_mul * protocol.enemy_hp_mul,
            item_spawn_mul=difficulty.drop_rate_mul * protocol.item_spawn_mul,
            phase_density_mul=self.current_phase.enemy_density_mul,
            phase_reward_mul=self.current_phase.event_weight_reward + 0.7,
        )
        self.respawn_ball()

    def respawn_ball(self):
        self.ball_system.respawn_ball(WIDTH // 2, HEIGHT // 2)
        self.effect_system.on_respawn()
        self.items = []
        self.state = GameState.WAITING_START

    def _spawn_interval_frames(self) -> int:
        density = max(0.2, self.current_phase.enemy_density_mul)
        base = int(90 / density)
        return max(15, base)

    def _spawn_enemy(self):
        elapsed_sec = self.run_elapsed_frames // 60
        self.current_phase = self.balance.get_phase_by_elapsed_sec(elapsed_sec)
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
        return int(base * difficulty.score_mul * protocol.base_score_mul)

    def _apply_enemy_damage(self, damage: int):
        difficulty = self.balance.get_difficulty(self.selected_mode)
        actual = max(1, math.ceil(damage * difficulty.enemy_damage_mul))
        elapsed_sec = self.run_elapsed_frames // 60
        if elapsed_sec < difficulty.early_guard_seconds:
            actual = max(1, math.ceil(actual * 0.5))
        self.lives -= actual
        if self.lives <= 0:
            if self.remaining_revives > 0:
                self.remaining_revives -= 1
                self.lives = 1
            else:
                self.state = GameState.GAME_OVER
                self.play_se(7)

    def update_enemies(self):
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
                self._apply_enemy_damage(enemy.damage)
                if self.state == GameState.GAME_OVER:
                    return
                self.play_se(5)
                continue
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
                if enemy.hp <= 0:
                    self.score += self._enemy_score(enemy.type)
                    self.combo += 1
                    self.combo_timer = 180
                    self.play_se(3)
        self.enemies = [e for e in self.enemies if e.hp > 0]

    def next_stage(self):
        self.stage += 1
        self.stage_clear_timer = 0
        self.effect_system.reset_stage_effects()
        self.setup_stage()
        self.play_stage_music()

    def play_stage_music(self):
        pyxel.stop(2)
        pyxel.play(2, [0, 1])

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

    def update(self):
        if pyxel.btnp(pyxel.KEY_R):
            self.reset()
            return
        if pyxel.btnp(pyxel.KEY_C):
            self.save_screen_shot()
        if self.shot_message_timer > 0:
            self.shot_message_timer -= 1

        if self.state == GameState.GAME_OVER:
            return

        if self.state == GameState.STAGE_CLEAR:
            self.stage_clear_timer -= 1
            if self.stage_clear_timer <= 0 or pyxel.btnp(pyxel.KEY_N):
                self.next_stage()
            return

        if self.state == GameState.WAITING_START:
            if self.run_elapsed_frames == 0:
                if pyxel.btnp(pyxel.KEY_1):
                    self.selected_mode = DifficultyMode.STORY
                    difficulty = self.balance.get_difficulty(self.selected_mode)
                    self.lives = difficulty.base_lives
                    self.remaining_revives = difficulty.revive_count
                if pyxel.btnp(pyxel.KEY_2):
                    self.selected_mode = DifficultyMode.STANDARD
                    difficulty = self.balance.get_difficulty(self.selected_mode)
                    self.lives = difficulty.base_lives
                    self.remaining_revives = difficulty.revive_count
                if pyxel.btnp(pyxel.KEY_3):
                    self.selected_mode = DifficultyMode.HARDCORE
                    difficulty = self.balance.get_difficulty(self.selected_mode)
                    self.lives = difficulty.base_lives
                    self.remaining_revives = difficulty.revive_count
                if pyxel.btnp(pyxel.KEY_TAB):
                    if self.selected_protocol == ProtocolType.FUSION:
                        self.selected_protocol = ProtocolType.REFLEX
                    else:
                        self.selected_protocol = ProtocolType.FUSION
                    self.setup_stage()
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

            hit_block, spawned_item = self.stage_field.collide_ball(ball)
            if hit_block:
                self.play_se(3)
            if spawned_item:
                self.items.append(spawned_item)

            alive_balls.append(ball)

        self.ball_system.balls = alive_balls
        if not self.ball_system.balls:
            self.lives -= 1
            if self.lives <= 0:
                if self.remaining_revives > 0:
                    self.remaining_revives -= 1
                    self.lives = 1
                else:
                    self.state = GameState.GAME_OVER
                    self.play_se(7)
                    return
            self.play_se(5)
            self.respawn_ball()
            return

        self.stage_field.update_moving_block()
        self.update_enemies()
        if self.state == GameState.GAME_OVER:
            return
        self.resolve_ball_enemy_collisions()
        if self.stage_field.all_cleared():
            self.state = GameState.STAGE_CLEAR
            self.stage_clear_timer = STAGE_CLEAR_WAIT
            self.play_se(6)
            return

        self.update_items()
        self.paddle_w, self.ball_speed_rate = self.effect_system.tick()
        self.paddle_x = max(0, min(WIDTH - self.paddle_w, self.paddle_x))

    def update_items(self):
        alive_items = []
        for item in self.items:
            item.y += ITEM_FALL_SPEED
            if (
                PADDLE_Y <= item.y <= PADDLE_Y + PADDLE_H
                and self.paddle_x <= item.x <= self.paddle_x + self.paddle_w
            ):
                self.effect_system.apply_item(item.type, self.ball_system)
                self.play_se(4)
                continue
            if item.y > HEIGHT + ITEM_SIZE:
                continue
            alive_items.append(item)
        self.items = alive_items

    def draw(self):
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
        self.draw_text(4, 4, "LEFT/RIGHT: Move  R: Reset  C:Shot", 7)
        self.draw_text(4, 12, "Hard:2  Item:W/S/M/F  Move:MV", 6)
        self.draw_text(
            4,
            HEIGHT - 16,
            f"Hard:{self.stage_field.hard_count} Item:{self.stage_field.item_count}",
            5,
        )
        self.draw_text(124, HEIGHT - 8, f"Stg:{self.stage}", 10)
        self.draw_text(118, 20, self.current_phase.label[:5], 12)
        self.draw_text(4, 20, f"{self.selected_mode.value}/{self.selected_protocol.value}", 12)

        for row in range(BLOCK_ROWS):
            for col in range(BLOCK_COLS):
                if self.stage_field.block_hp[row][col]:
                    bx = BLOCK_OFFSET_X + col * (BLOCK_W + BLOCK_GAP)
                    by = BLOCK_OFFSET_Y + row * (BLOCK_H + BLOCK_GAP)
                    block_color = 2 if self.stage_field.block_hp[row][col] == 2 else 8 + row
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
            pyxel.rect(item.x - ITEM_SIZE // 2, item.y - ITEM_SIZE // 2, ITEM_SIZE, ITEM_SIZE, color)

        for enemy in self.enemies:
            color = 8
            if enemy.type == EnemyType.SPLITTER:
                color = 14
            if enemy.type == EnemyType.SNIPER_ORB:
                color = 11
            if enemy.type == EnemyType.SHIELD_NODE:
                color = 2
            pyxel.circ(enemy.x, enemy.y, 3, color)

        pyxel.rect(self.paddle_x, PADDLE_Y, self.paddle_w, PADDLE_H, 10)
        for ball in self.ball_system.balls:
            pyxel.circ(ball.x, ball.y, BALL_R, 7)

        self.draw_text(4, HEIGHT - 8, f"Balls:{len(self.ball_system.balls)}", 7)
        self.draw_text(62, HEIGHT - 8, f"Life:{self.lives}", 8)
        self.draw_text(100, HEIGHT - 8, f"Rv:{self.remaining_revives}", 14)
        self.draw_text(4, HEIGHT - 24, f"Score:{self.score}", 10)
        self.draw_text(86, HEIGHT - 24, f"Combo:{self.combo}", 6)

        if self.effect_system.effect_wide_timer > 0:
            self.draw_text(
                40,
                HEIGHT - 32,
                f"W{self.effect_system.effect_wide_level}:{self.effect_system.effect_wide_timer // 60}s",
                9,
            )
        if self.effect_system.effect_slow_timer > 0:
            self.draw_text(
                86,
                HEIGHT - 32,
                f"S{self.effect_system.effect_slow_level}:{self.effect_system.effect_slow_timer // 60}s",
                11,
            )
        if self.effect_system.effect_fast_timer > 0:
            self.draw_text(
                132,
                HEIGHT - 32,
                f"F{self.effect_system.effect_fast_level}:{self.effect_system.effect_fast_timer // 60}s",
                8,
            )
        if self.shot_message_timer > 0:
            self.draw_text(4, 20, self.shot_message, 10)

        if self.state == GameState.STAGE_CLEAR:
            self.draw_text(43, 56, f"STAGE {self.stage} CLEAR!", 11)
            self.draw_text(28, 66, "Next: N or auto", 7)
        if self.state == GameState.WAITING_START:
            pyxel.rect(8, 28, 144, 72, 0)
            pyxel.rectb(8, 28, 144, 72, 7)
            self.draw_text(14, 36, "あそびかた", 10, jp=True)
            if self.run_elapsed_frames == 0:
                self.draw_text(14, 48, "1:Story 2:Std 3:Hard", 7)
                self.draw_text(14, 58, f"Mode:{self.selected_mode.value}", 7)
                self.draw_text(14, 68, f"Proto:{self.selected_protocol.value} (TAB)", 7)
                self.draw_text(14, 78, "W/S/M/F items + SF phase", 7)
                self.draw_text(14, 90, "SPACE:start  C:shot", 10)
            else:
                self.draw_text(14, 48, "ひだり/みぎ いどう", 7, jp=True, small_jp=True)
                self.draw_text(14, 58, "ぜんぶこわして クリア", 7, jp=True, small_jp=True)
                self.draw_text(14, 68, "W:バー  S:スロー", 7, jp=True, small_jp=True)
                self.draw_text(14, 78, "M:+たま  F:はやい(2~)", 7, jp=True, small_jp=True)
                self.draw_text(14, 90, "SPACE:スタート C:保存", 10, jp=True, small_jp=True)
        if self.state == GameState.GAME_OVER:
            self.draw_text(51, 58, "GAME OVER", 8)
            self.draw_text(43, 68, "Press R to retry", 7)

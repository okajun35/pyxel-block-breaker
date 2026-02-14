from datetime import datetime
from pathlib import Path
import time
import shutil
import os

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
from game.entities import FallingItem
from game.enums import GameState, ItemType
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
        self.ball_system = BallSystem()
        self.effect_system = EffectSystem()
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
        self.lives = START_LIVES
        self.stage = 1
        self.state = GameState.WAITING_START
        self.stage_clear_timer = 0
        self.shot_message = ""
        self.shot_message_timer = 0
        self.items: list[FallingItem] = []
        self.effect_system.reset_all()
        self.setup_stage()

    def setup_stage(self):
        self.stage_field.setup(self.stage)
        self.respawn_ball()

    def respawn_ball(self):
        self.ball_system.respawn_ball(WIDTH // 2, HEIGHT // 2)
        self.effect_system.on_respawn()
        self.items = []
        self.state = GameState.WAITING_START

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
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.state = GameState.PLAYING
            return

        if pyxel.btn(pyxel.KEY_LEFT):
            self.paddle_x -= PADDLE_SPEED
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.paddle_x += PADDLE_SPEED
        self.paddle_x = max(0, min(WIDTH - self.paddle_w, self.paddle_x))

        alive_balls = []
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
                and PADDLE_Y <= ball.y + BALL_R <= PADDLE_Y + PADDLE_H
                and self.paddle_x <= ball.x <= self.paddle_x + self.paddle_w
            ):
                offset = (ball.x - (self.paddle_x + self.paddle_w / 2)) / (self.paddle_w / 2)
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
                self.state = GameState.GAME_OVER
                self.play_se(7)
                return
            self.play_se(5)
            self.respawn_ball()
            return

        self.stage_field.update_moving_block()
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

        pyxel.rect(self.paddle_x, PADDLE_Y, self.paddle_w, PADDLE_H, 10)
        for ball in self.ball_system.balls:
            pyxel.circ(ball.x, ball.y, BALL_R, 7)

        self.draw_text(4, HEIGHT - 8, f"Balls:{len(self.ball_system.balls)}", 7)
        self.draw_text(62, HEIGHT - 8, f"Life:{self.lives}", 8)

        if self.effect_system.effect_wide_timer > 0:
            self.draw_text(
                40,
                HEIGHT - 24,
                f"W{self.effect_system.effect_wide_level}:{self.effect_system.effect_wide_timer // 60}s",
                9,
            )
        if self.effect_system.effect_slow_timer > 0:
            self.draw_text(
                86,
                HEIGHT - 24,
                f"S{self.effect_system.effect_slow_level}:{self.effect_system.effect_slow_timer // 60}s",
                11,
            )
        if self.effect_system.effect_fast_timer > 0:
            self.draw_text(
                132,
                HEIGHT - 24,
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
            self.draw_text(14, 48, "ひだり/みぎ いどう", 7, jp=True, small_jp=True)
            self.draw_text(14, 58, "ぜんぶこわして クリア", 7, jp=True, small_jp=True)
            self.draw_text(14, 68, "W:バー  S:スロー", 7, jp=True, small_jp=True)
            self.draw_text(14, 78, "M:+たま  F:はやい(2~)", 7, jp=True, small_jp=True)
            self.draw_text(14, 90, "SPACE:スタート C:保存", 10, jp=True, small_jp=True)
        if self.state == GameState.GAME_OVER:
            self.draw_text(51, 58, "GAME OVER", 8)
            self.draw_text(43, 68, "Press R to retry", 7)

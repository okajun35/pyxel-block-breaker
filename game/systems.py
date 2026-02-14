import math

import pyxel

from game.constants import (
    BALL_R,
    BASE_BALL_SPEED,
    BASE_PADDLE_W,
    BASE_SPEED_RATE,
    BLOCK_COLS,
    BLOCK_GAP,
    BLOCK_H,
    BLOCK_OFFSET_X,
    BLOCK_OFFSET_Y,
    BLOCK_ROWS,
    BLOCK_W,
    FAST_BASE_RATE,
    FAST_LEVEL_MAX,
    HARD_BLOCK_COUNT,
    HARD_BLOCK_INC_PER_STAGE,
    HEIGHT,
    ITEM_BLOCK_COUNT,
    ITEM_BLOCK_INC_PER_STAGE,
    ITEM_BONUS_DURATION,
    ITEM_DURATION,
    MAX_BALLS,
    MOVING_BLOCK_H,
    MOVING_BLOCK_SPEED,
    MOVING_BLOCK_W,
    MOVING_BLOCK_Y,
    SLOW_LEVEL_MAX,
    START_SLOW_DURATION,
    START_SLOW_RATE,
    WIDE_LEVEL_MAX,
)
from game.entities import Ball, FallingItem, MovingBlock
from game.enums import ItemType


class BallSystem:
    def __init__(self):
        self.balls: list[Ball] = []

    def normalized_velocity(self, vx: float, vy: float) -> tuple[float, float]:
        size = math.sqrt(vx * vx + vy * vy)
        if size == 0:
            return 0.0, -BASE_BALL_SPEED
        scale = BASE_BALL_SPEED / size
        return vx * scale, vy * scale

    def respawn_ball(self, x: int, y: int) -> None:
        vx, vy = self.normalized_velocity(1.0, -1.0)
        self.balls = [Ball(x=x, y=y, vx=vx, vy=vy)]

    def add_balls(self, count: int) -> None:
        for _ in range(count):
            if len(self.balls) >= MAX_BALLS or not self.balls:
                return
            base = self.balls[0]
            new_vx = -base.vx + pyxel.rndf(-0.4, 0.4)
            new_vy = -abs(base.vy)
            new_vx, new_vy = self.normalized_velocity(new_vx, new_vy)
            self.balls.append(Ball(x=base.x, y=base.y, vx=new_vx, vy=new_vy))


class EffectSystem:
    def __init__(self):
        self.effect_wide_timer = 0
        self.effect_slow_timer = 0
        self.effect_fast_timer = 0
        self.effect_wide_level = 0
        self.effect_slow_level = 0
        self.effect_fast_level = 0
        self.multi_level = 0
        self.start_slow_timer = 0

    def reset_all(self) -> None:
        self.effect_wide_timer = 0
        self.effect_slow_timer = 0
        self.effect_fast_timer = 0
        self.effect_wide_level = 0
        self.effect_slow_level = 0
        self.effect_fast_level = 0
        self.multi_level = 0
        self.start_slow_timer = 0

    def reset_stage_effects(self) -> None:
        self.effect_wide_timer = 0
        self.effect_slow_timer = 0
        self.effect_fast_timer = 0
        self.effect_wide_level = 0
        self.effect_slow_level = 0
        self.effect_fast_level = 0

    def on_respawn(self) -> None:
        self.start_slow_timer = START_SLOW_DURATION

    def apply_item(self, item_type: ItemType, ball_system: BallSystem) -> None:
        if item_type == ItemType.WIDE:
            self.effect_wide_level = min(WIDE_LEVEL_MAX, self.effect_wide_level + 1)
            if self.effect_wide_timer > 0:
                self.effect_wide_timer += ITEM_BONUS_DURATION
            else:
                self.effect_wide_timer = ITEM_DURATION
        if item_type == ItemType.SLOW:
            self.effect_slow_level = min(SLOW_LEVEL_MAX, self.effect_slow_level + 1)
            if self.effect_slow_timer > 0:
                self.effect_slow_timer += ITEM_BONUS_DURATION
            else:
                self.effect_slow_timer = ITEM_DURATION
        if item_type == ItemType.MULTI:
            self.multi_level = min(3, self.multi_level + 1)
            ball_system.add_balls(self.multi_level)
        if item_type == ItemType.FAST:
            self.effect_fast_level = min(FAST_LEVEL_MAX, self.effect_fast_level + 1)
            if self.effect_fast_timer > 0:
                self.effect_fast_timer += ITEM_BONUS_DURATION
            else:
                self.effect_fast_timer = ITEM_DURATION

    def tick(self) -> tuple[int, float]:
        if self.effect_wide_timer > 0:
            self.effect_wide_timer -= 1
            paddle_w = BASE_PADDLE_W + 12 + (self.effect_wide_level - 1) * 6
        else:
            paddle_w = BASE_PADDLE_W
            self.effect_wide_level = 0

        speed_rate = BASE_SPEED_RATE
        if self.effect_slow_timer > 0:
            self.effect_slow_timer -= 1
            slow_rate = 0.65 - (self.effect_slow_level - 1) * 0.1
            speed_rate = min(speed_rate, max(0.35, slow_rate))
        else:
            self.effect_slow_level = 0

        if self.start_slow_timer > 0:
            self.start_slow_timer -= 1
            speed_rate = min(speed_rate, START_SLOW_RATE)

        if self.effect_fast_timer > 0:
            self.effect_fast_timer -= 1
            fast_rate = FAST_BASE_RATE + (self.effect_fast_level - 1) * 0.12
            speed_rate = max(speed_rate, min(1.35, fast_rate))
        else:
            self.effect_fast_level = 0

        return paddle_w, speed_rate


class StageField:
    def __init__(self):
        self.block_hp: list[list[int]] = []
        self.item_blocks: list[list[ItemType | None]] = []
        self.moving_block = MovingBlock(x=0, y=0, vx=0.0, hp=0)
        self.hard_count = 0
        self.item_count = 0

    def setup(
        self,
        stage: int,
        enemy_hp_mul: float = 1.0,
        item_spawn_mul: float = 1.0,
        phase_density_mul: float = 1.0,
        phase_reward_mul: float = 1.0,
    ) -> None:
        self.block_hp = [[1 for _ in range(BLOCK_COLS)] for _ in range(BLOCK_ROWS)]
        self.item_blocks = [[None for _ in range(BLOCK_COLS)] for _ in range(BLOCK_ROWS)]
        moving_hp = min(6, max(1, int((1 + stage) * enemy_hp_mul)))
        moving_speed = min(1.8, MOVING_BLOCK_SPEED + 0.1 * (stage - 1))
        self.moving_block = MovingBlock(
            x=80 - MOVING_BLOCK_W // 2,
            y=MOVING_BLOCK_Y,
            vx=moving_speed,
            hp=moving_hp,
        )
        total_blocks = BLOCK_ROWS * BLOCK_COLS
        hard_base = HARD_BLOCK_COUNT + (stage - 1) * HARD_BLOCK_INC_PER_STAGE
        item_base = ITEM_BLOCK_COUNT + (stage - 1) * ITEM_BLOCK_INC_PER_STAGE
        self.hard_count = min(
            total_blocks - 1,
            max(1, int(hard_base * enemy_hp_mul * phase_density_mul)),
        )
        self.item_count = min(
            total_blocks,
            max(1, int(item_base * item_spawn_mul * phase_reward_mul)),
        )
        self.place_hard_blocks(self.hard_count)
        self.place_item_blocks(self.item_count, stage)

    def place_hard_blocks(self, target: int) -> None:
        placed = 0
        while placed < target:
            row = pyxel.rndi(0, BLOCK_ROWS - 1)
            col = pyxel.rndi(0, BLOCK_COLS - 1)
            if self.block_hp[row][col] == 2:
                continue
            self.block_hp[row][col] = 2
            placed += 1

    def place_item_blocks(self, target: int, stage: int) -> None:
        placed = 0
        while placed < target:
            row = pyxel.rndi(0, BLOCK_ROWS - 1)
            col = pyxel.rndi(0, BLOCK_COLS - 1)
            if self.item_blocks[row][col] is not None:
                continue
            max_roll = 3 if stage >= 2 else 2
            item_roll = pyxel.rndi(0, max_roll)
            if item_roll == 0:
                self.item_blocks[row][col] = ItemType.WIDE
            elif item_roll == 1:
                self.item_blocks[row][col] = ItemType.SLOW
            elif item_roll == 2:
                self.item_blocks[row][col] = ItemType.MULTI
            else:
                self.item_blocks[row][col] = ItemType.FAST
            placed += 1

    def collide_ball(self, ball: Ball) -> tuple[bool, FallingItem | None]:
        if self.moving_block.hp > 0:
            mx = self.moving_block.x
            my = self.moving_block.y
            if mx <= ball.x <= mx + MOVING_BLOCK_W and my <= ball.y <= my + MOVING_BLOCK_H:
                ball.vy *= -1
                self.moving_block.hp -= 1
                return True, None

        for row in range(BLOCK_ROWS):
            for col in range(BLOCK_COLS):
                if self.block_hp[row][col] == 0:
                    continue
                bx = BLOCK_OFFSET_X + col * (BLOCK_W + BLOCK_GAP)
                by = BLOCK_OFFSET_Y + row * (BLOCK_H + BLOCK_GAP)
                if bx <= ball.x <= bx + BLOCK_W and by <= ball.y <= by + BLOCK_H:
                    ball.vy *= -1
                    self.block_hp[row][col] -= 1
                    if self.block_hp[row][col] == 0:
                        item_type = self.item_blocks[row][col]
                        if item_type:
                            self.item_blocks[row][col] = None
                            return True, FallingItem(
                                x=bx + BLOCK_W // 2,
                                y=by + BLOCK_H // 2,
                                type=item_type,
                            )
                    return True, None
        return False, None

    def update_moving_block(self) -> None:
        if self.moving_block.hp == 0:
            return
        self.moving_block.x += self.moving_block.vx
        if self.moving_block.x <= 0:
            self.moving_block.x = 0
            self.moving_block.vx *= -1
        if self.moving_block.x >= 160 - MOVING_BLOCK_W:
            self.moving_block.x = 160 - MOVING_BLOCK_W
            self.moving_block.vx *= -1

    def all_cleared(self) -> bool:
        return (
            all(v == 0 for row in self.block_hp for v in row)
            and self.moving_block.hp == 0
        )

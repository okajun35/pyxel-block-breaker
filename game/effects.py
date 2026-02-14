from dataclasses import dataclass


@dataclass
class HitEffect:
    x: float
    y: float
    vx: float
    vy: float
    ttl: int
    color: int


class HitEffectSystem:
    def __init__(self):
        self.effects: list[HitEffect] = []

    def spawn_block_hit(self, x: float, y: float):
        self.effects.extend(
            [
                HitEffect(x, y, -0.8, -0.5, 10, 7),
                HitEffect(x, y, 0.8, -0.5, 10, 7),
                HitEffect(x, y, -0.4, 0.7, 8, 10),
                HitEffect(x, y, 0.4, 0.7, 8, 10),
            ]
        )

    def spawn_enemy_hit(self, x: float, y: float, boss: bool):
        speed = 1.2 if boss else 0.9
        count = 10 if boss else 6
        for i in range(count):
            dx = (-1 + (i % 5) * 0.5) * speed
            dy = (-1 + (i // 5) * 0.6) * speed
            self.effects.append(HitEffect(x, y, dx, dy, 12 if boss else 9, 8 if boss else 14))

    def tick(self):
        alive: list[HitEffect] = []
        for e in self.effects:
            e.x += e.vx
            e.y += e.vy
            e.vy += 0.04
            e.ttl -= 1
            if e.ttl > 0:
                alive.append(e)
        self.effects = alive

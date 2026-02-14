from dataclasses import dataclass

from game.enums import ItemType


@dataclass(frozen=True)
class StageRole:
    code: str
    label: str
    enemy_spawn_rate_mul: float
    moving_speed_mul: float
    preferred_item: ItemType | None


ROLES = [
    StageRole("intro", "Intro", 0.85, 0.9, ItemType.WIDE),
    StageRole("evasion", "Evasion", 1.2, 1.35, ItemType.SLOW),
    StageRole("rush", "Rush", 1.35, 1.0, ItemType.MULTI),
    StageRole("control", "Control", 1.0, 0.95, ItemType.FAST),
]


def stage_role(stage: int) -> StageRole:
    idx = ((max(1, stage) - 1) % len(ROLES))
    return ROLES[idx]

from dataclasses import dataclass
from pathlib import Path

from game.constants import ROOT_DIR
from game.enums import EnemyType


@dataclass(frozen=True)
class SpriteRect:
    u: int
    v: int
    w: int
    h: int


class AssetCatalog:
    def __init__(self, root_dir: Path | None = None):
        self.root_dir = Path(root_dir) if root_dir else ROOT_DIR / "assets"

    def asset_path(self, relative_path: str) -> Path:
        return self.root_dir / relative_path

    def required_files(self) -> list[str]:
        backgrounds = [
            f"backgrounds/starfield_{idx:02d}.png"
            for idx in range(1, 5)
        ]
        return [
            "sprites/sheet.png",
            "ui/panel_start.png",
            *backgrounds,
        ]

    def missing_required_files(self) -> list[str]:
        return [
            rel for rel in self.required_files()
            if not self.asset_path(rel).exists()
        ]

    def stage_background_relative(self, stage: int) -> str:
        idx = ((max(1, stage) - 1) % 4) + 1
        return f"backgrounds/starfield_{idx:02d}.png"


class SpriteSheet:
    BLOCK_NORMAL = SpriteRect(0, 0, 18, 6)
    BLOCK_HARD = SpriteRect(18, 0, 18, 6)
    MOVING_BLOCK = SpriteRect(36, 0, 18, 6)
    ITEM_W = SpriteRect(0, 8, 6, 6)
    ITEM_S = SpriteRect(6, 8, 6, 6)
    ITEM_M = SpriteRect(12, 8, 6, 6)
    ITEM_F = SpriteRect(18, 8, 6, 6)
    ENEMY_DRONE_A = SpriteRect(0, 16, 8, 8)
    ENEMY_DRONE_B = SpriteRect(0, 24, 8, 8)
    ENEMY_SPLITTER_A = SpriteRect(8, 16, 8, 8)
    ENEMY_SPLITTER_B = SpriteRect(8, 24, 8, 8)
    ENEMY_SNIPER_A = SpriteRect(16, 16, 8, 8)
    ENEMY_SNIPER_B = SpriteRect(16, 24, 8, 8)
    ENEMY_SHIELD_A = SpriteRect(24, 16, 8, 8)
    ENEMY_SHIELD_B = SpriteRect(24, 24, 8, 8)
    ENEMY_BOSS_A = SpriteRect(32, 16, 12, 12)
    ENEMY_BOSS_B = SpriteRect(48, 16, 12, 12)


class EnemySpriteAnimator:
    @staticmethod
    def frame_for(enemy_type: EnemyType, frame_count: int) -> SpriteRect:
        if enemy_type == EnemyType.NULL_CORE_BOSS:
            blink = (frame_count // 10) % 2
            return SpriteSheet.ENEMY_BOSS_B if blink else SpriteSheet.ENEMY_BOSS_A

        blink = (frame_count // 6) % 2
        if enemy_type == EnemyType.SPLITTER:
            return SpriteSheet.ENEMY_SPLITTER_B if blink else SpriteSheet.ENEMY_SPLITTER_A
        if enemy_type == EnemyType.SNIPER_ORB:
            return SpriteSheet.ENEMY_SNIPER_B if blink else SpriteSheet.ENEMY_SNIPER_A
        if enemy_type == EnemyType.SHIELD_NODE:
            return SpriteSheet.ENEMY_SHIELD_B if blink else SpriteSheet.ENEMY_SHIELD_A
        return SpriteSheet.ENEMY_DRONE_B if blink else SpriteSheet.ENEMY_DRONE_A

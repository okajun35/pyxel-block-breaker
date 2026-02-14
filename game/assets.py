from dataclasses import dataclass
from pathlib import Path

from game.constants import ROOT_DIR


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
        return [
            "sprites/sheet.png",
            "ui/panel_start.png",
            "backgrounds/starfield.png",
        ]

    def missing_required_files(self) -> list[str]:
        return [
            rel for rel in self.required_files()
            if not self.asset_path(rel).exists()
        ]


class SpriteSheet:
    BLOCK_NORMAL = SpriteRect(0, 0, 18, 6)
    BLOCK_HARD = SpriteRect(18, 0, 18, 6)
    MOVING_BLOCK = SpriteRect(36, 0, 18, 6)
    ITEM_W = SpriteRect(0, 8, 6, 6)
    ITEM_S = SpriteRect(6, 8, 6, 6)
    ITEM_M = SpriteRect(12, 8, 6, 6)
    ITEM_F = SpriteRect(18, 8, 6, 6)
    ENEMY_DRONE = SpriteRect(0, 16, 8, 8)
    ENEMY_SPLITTER = SpriteRect(8, 16, 8, 8)
    ENEMY_SNIPER = SpriteRect(16, 16, 8, 8)
    ENEMY_SHIELD = SpriteRect(24, 16, 8, 8)
    ENEMY_BOSS = SpriteRect(32, 16, 12, 12)

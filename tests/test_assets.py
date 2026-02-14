import unittest
from pathlib import Path

from game.assets import AssetCatalog, EnemySpriteAnimator, SpriteSheet
from game.enums import EnemyType


class AssetCatalogTests(unittest.TestCase):
    def test_required_assets_exist(self):
        catalog = AssetCatalog()
        missing = catalog.missing_required_files()
        self.assertEqual(missing, [])

    def test_has_enemy_ui_background_assets(self):
        catalog = AssetCatalog()
        required = catalog.required_files()
        self.assertIn("sprites/sheet.png", required)
        self.assertIn("ui/panel_start.png", required)
        self.assertIn("backgrounds/starfield_01.png", required)
        self.assertIn("backgrounds/starfield_04.png", required)

    def test_asset_path_is_under_assets(self):
        catalog = AssetCatalog()
        path = catalog.asset_path("sprites/sheet.png")
        self.assertEqual(path, Path(catalog.root_dir) / "sprites" / "sheet.png")

    def test_stage_background_cycles(self):
        catalog = AssetCatalog()
        self.assertEqual(catalog.stage_background_relative(1), "backgrounds/starfield_01.png")
        self.assertEqual(catalog.stage_background_relative(4), "backgrounds/starfield_04.png")
        self.assertEqual(catalog.stage_background_relative(5), "backgrounds/starfield_01.png")


class EnemySpriteAnimatorTests(unittest.TestCase):
    def test_non_boss_enemy_alternates_every_6_frames(self):
        f0 = EnemySpriteAnimator.frame_for(EnemyType.DRONE, frame_count=0)
        f1 = EnemySpriteAnimator.frame_for(EnemyType.DRONE, frame_count=7)
        self.assertEqual(f0, SpriteSheet.ENEMY_DRONE_A)
        self.assertEqual(f1, SpriteSheet.ENEMY_DRONE_B)

    def test_boss_enemy_alternates_every_10_frames(self):
        f0 = EnemySpriteAnimator.frame_for(EnemyType.NULL_CORE_BOSS, frame_count=0)
        f1 = EnemySpriteAnimator.frame_for(EnemyType.NULL_CORE_BOSS, frame_count=11)
        self.assertEqual(f0, SpriteSheet.ENEMY_BOSS_A)
        self.assertEqual(f1, SpriteSheet.ENEMY_BOSS_B)


if __name__ == "__main__":
    unittest.main()

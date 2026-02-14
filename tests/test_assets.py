import unittest
from pathlib import Path

from game.assets import AssetCatalog


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
        self.assertIn("backgrounds/starfield.png", required)

    def test_asset_path_is_under_assets(self):
        catalog = AssetCatalog()
        path = catalog.asset_path("sprites/sheet.png")
        self.assertEqual(path, Path(catalog.root_dir) / "sprites" / "sheet.png")


if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import patch

from game.constants import ITEM_BONUS_DURATION, ITEM_DURATION
from game.enums import ItemType
from game.systems import BallSystem, EffectSystem, StageField


class StageFieldItemTests(unittest.TestCase):
    def test_fast_item_appears_from_stage_2(self):
        field = StageField()
        field.item_blocks = [[None for _ in range(8)] for _ in range(4)]

        with patch("game.systems.pyxel.rndi", side_effect=lambda a, b: b):
            field.place_item_blocks(target=1, stage=2)

        flat = [cell for row in field.item_blocks for cell in row]
        self.assertIn(ItemType.FAST, flat)

    def test_fast_item_not_used_on_stage_1(self):
        field = StageField()
        field.item_blocks = [[None for _ in range(8)] for _ in range(4)]

        with patch("game.systems.pyxel.rndi", side_effect=lambda a, b: b):
            field.place_item_blocks(target=1, stage=1)

        flat = [cell for row in field.item_blocks for cell in row if cell is not None]
        self.assertTrue(flat)
        self.assertNotIn(ItemType.FAST, flat)


class EffectTimerTests(unittest.TestCase):
    def test_same_item_extends_effect_time(self):
        effects = EffectSystem()
        balls = BallSystem()
        balls.respawn_ball(80, 60)

        effects.apply_item(ItemType.SLOW, balls)
        first = effects.effect_slow_timer
        effects.apply_item(ItemType.SLOW, balls)

        self.assertEqual(first, ITEM_DURATION)
        self.assertEqual(effects.effect_slow_timer, ITEM_DURATION + ITEM_BONUS_DURATION)


if __name__ == "__main__":
    unittest.main()

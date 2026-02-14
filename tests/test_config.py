import unittest

from game.config import BalanceConfig
from game.enums import DifficultyMode, EnemyType, ItemType, ProtocolType


class ConfigTests(unittest.TestCase):
    def test_load_profiles(self):
        cfg = BalanceConfig()
        self.assertIn(DifficultyMode.STORY, cfg.difficulty_profiles)
        self.assertIn(DifficultyMode.STANDARD, cfg.difficulty_profiles)
        self.assertIn(DifficultyMode.HARDCORE, cfg.difficulty_profiles)
        self.assertIn(ProtocolType.FUSION, cfg.protocol_profiles)
        self.assertIn(ProtocolType.REFLEX, cfg.protocol_profiles)
        self.assertGreaterEqual(len(cfg.run_phases), 5)

    def test_phase_lookup(self):
        cfg = BalanceConfig()
        p1 = cfg.get_phase_by_elapsed_sec(0)
        p5 = cfg.get_phase_by_elapsed_sec(1700)
        self.assertEqual(p1.phase_id, 1)
        self.assertEqual(p5.phase_id, 5)

    def test_item_effect_profiles_loaded(self):
        cfg = BalanceConfig()
        wide = cfg.item_effect_profiles[ItemType.WIDE]
        fast = cfg.item_effect_profiles[ItemType.FAST]
        self.assertEqual(wide.base_duration_sec, 8)
        self.assertEqual(wide.same_item_bonus_sec, 10)
        self.assertEqual(fast.stage_min, 2)

    def test_enemy_profiles_loaded(self):
        cfg = BalanceConfig()
        drone = cfg.enemy_profiles[EnemyType.DRONE]
        boss = cfg.enemy_profiles[EnemyType.NULL_CORE_BOSS]
        self.assertEqual(drone.base_hp, 30)
        self.assertEqual(boss.collision_damage, 2)


if __name__ == "__main__":
    unittest.main()

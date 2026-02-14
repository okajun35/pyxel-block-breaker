import unittest

from game.config import BalanceConfig
from game.enums import DifficultyMode, ProtocolType


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


if __name__ == "__main__":
    unittest.main()

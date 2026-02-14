import unittest

from game.coaching import suggest_next_actions
from game.run_report import RunReport


class CoachingTests(unittest.TestCase):
    def test_suggest_enemy_focus_when_enemy_damage_high(self):
        report = RunReport(time_sec=90, max_combo=3, damage_taken=6, cleared_phase=1, score=300)
        tips = suggest_next_actions(report, ["enemy_reach:drone", "enemy_reach:shield_node"])
        self.assertTrue(any("敵" in t for t in tips))

    def test_suggest_combo_focus_when_combo_low(self):
        report = RunReport(time_sec=180, max_combo=1, damage_taken=1, cleared_phase=2, score=400)
        tips = suggest_next_actions(report, ["ball_drop"])
        self.assertTrue(any("コンボ" in t for t in tips))


if __name__ == "__main__":
    unittest.main()

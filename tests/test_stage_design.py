import unittest

from game.stage_design import stage_role


class StageDesignTests(unittest.TestCase):
    def test_stage_role_cycles(self):
        self.assertEqual(stage_role(1).code, "intro")
        self.assertEqual(stage_role(2).code, "evasion")
        self.assertEqual(stage_role(3).code, "rush")
        self.assertEqual(stage_role(4).code, "control")
        self.assertEqual(stage_role(5).code, "intro")


if __name__ == "__main__":
    unittest.main()

import os
import unittest

from game.automation import AutoRunConfig, parse_frames


class AutomationTests(unittest.TestCase):
    def test_parse_frames(self):
        self.assertEqual(parse_frames("10, 20,50"), [10, 20, 50])
        self.assertEqual(parse_frames(""), [])
        self.assertEqual(parse_frames("abc,30"), [30])

    def test_config_disabled_by_default(self):
        cfg = AutoRunConfig.from_env({})
        self.assertFalse(cfg.enabled)
        self.assertEqual(cfg.capture_frames, [])
        self.assertEqual(cfg.exit_frame, 0)

    def test_config_from_env(self):
        env = {
            "PYXEL_AUTORUN": "1",
            "PYXEL_AUTOCAP_FRAMES": "30,120",
            "PYXEL_AUTOEXIT_FRAME": "180",
        }
        cfg = AutoRunConfig.from_env(env)
        self.assertTrue(cfg.enabled)
        self.assertEqual(cfg.capture_frames, [30, 120])
        self.assertEqual(cfg.exit_frame, 180)


if __name__ == "__main__":
    unittest.main()

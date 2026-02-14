import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from game.app import App
from game.constants import BASE_SPEED_RATE


class DummyEffectSystem:
    def reset_all(self):
        return None


class AppInitTests(unittest.TestCase):
    def test_reset_initializes_ball_speed_rate(self):
        app = App.__new__(App)
        app.effect_system = DummyEffectSystem()
        app.setup_stage = lambda: None

        App.reset(app)

        self.assertEqual(app.ball_speed_rate, BASE_SPEED_RATE)

    def test_save_screenshot_creates_tmp_jp_png(self):
        app = App.__new__(App)
        app.shot_message = ""
        app.shot_message_timer = 0

        with tempfile.TemporaryDirectory() as d:
            cwd = Path.cwd()
            try:
                Path(d).mkdir(parents=True, exist_ok=True)
                os.chdir(d)

                def fake_capture(path):
                    Path(path).write_bytes(b"fake")

                app.capture_screen = fake_capture
                with patch("game.app.TMP_DIR", Path("tmp")):
                    App.save_screen_shot(app)

                self.assertTrue(Path("tmp/jp.png").exists())
                self.assertIn("tmp/jp.png", app.shot_message)
            finally:
                os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()

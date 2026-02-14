import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from game.app import App
from game.config import BalanceConfig
from game.enums import DifficultyMode, GameState, ProtocolType
from game.constants import BASE_SPEED_RATE


class DummyEffectSystem:
    def reset_all(self):
        return None


class DummyProgression:
    class State:
        life_upgrade_level = 2
        core_gain_upgrade_level = 1
        paddle_upgrade_level = 2

    state = State()


class DummyMetrics:
    def __init__(self):
        self.rows = []

    def append(self, **kwargs):
        self.rows.append(kwargs)


class AppInitTests(unittest.TestCase):
    def test_reset_initializes_ball_speed_rate(self):
        app = App.__new__(App)
        app.effect_system = DummyEffectSystem()
        app.balance = BalanceConfig()
        app.selected_mode = DifficultyMode.STANDARD
        app.selected_protocol = ProtocolType.FUSION
        app.setup_stage = lambda: None

        App.reset(app)

        self.assertEqual(app.ball_speed_rate, BASE_SPEED_RATE)
        self.assertEqual(app.state, GameState.TITLE)

    def test_reset_applies_life_upgrade_level(self):
        app = App.__new__(App)
        app.effect_system = DummyEffectSystem()
        app.balance = BalanceConfig()
        app.selected_mode = DifficultyMode.STANDARD
        app.selected_protocol = ProtocolType.FUSION
        app.progression = DummyProgression()
        app.setup_stage = lambda: None

        App.reset(app)

        self.assertEqual(app.lives, 5)

    def test_upgrade_helpers(self):
        app = App.__new__(App)
        app.progression = DummyProgression()
        self.assertEqual(App._core_gain_multiplier(app), 1.2)
        self.assertEqual(App._paddle_upgrade_bonus(app), 8)

    def test_record_run_metric_once(self):
        class Report:
            time_sec = 10
            score = 100
            max_combo = 4
            damage_taken = 2
            cleared_phase = 1

        app = App.__new__(App)
        app.run_metric_recorded = False
        app.metrics = DummyMetrics()
        app.selected_mode = DifficultyMode.STANDARD
        app.selected_protocol = ProtocolType.FUSION
        app.last_report = Report()

        App._record_run_metric(app)
        App._record_run_metric(app)

        self.assertEqual(len(app.metrics.rows), 1)

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

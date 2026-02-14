import unittest

from game.run_report import build_run_report


class RunReportTests(unittest.TestCase):
    def test_build_report(self):
        report = build_run_report(
            elapsed_frames=3661,
            max_combo=12,
            damage_taken=7,
            cleared_phase=3,
            score=1234,
        )
        self.assertEqual(report.time_sec, 61)
        self.assertEqual(report.max_combo, 12)
        self.assertEqual(report.damage_taken, 7)
        self.assertEqual(report.cleared_phase, 3)
        self.assertEqual(report.score, 1234)


if __name__ == "__main__":
    unittest.main()

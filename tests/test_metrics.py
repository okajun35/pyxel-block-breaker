import tempfile
import unittest
from pathlib import Path

from game.metrics import MetricsStore


class MetricsTests(unittest.TestCase):
    def test_append_and_load(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "metrics.jsonl"
            store = MetricsStore(path)
            store.append(
                mode="story",
                protocol="fusion",
                time_sec=120,
                score=500,
                max_combo=6,
                damage=4,
                phase=2,
            )
            rows = store.read_all()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["mode"], "story")

    def test_summary_ratios(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "metrics.jsonl"
            store = MetricsStore(path)
            store.append("story", "fusion", 100, 100, 3, 2, 1)
            store.append("standard", "reflex", 110, 120, 4, 3, 2)
            summary = store.summary()
            self.assertEqual(summary["runs"], 2)
            self.assertEqual(summary["protocol_count"]["fusion"], 1)
            self.assertEqual(summary["protocol_count"]["reflex"], 1)


if __name__ == "__main__":
    unittest.main()

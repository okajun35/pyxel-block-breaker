import tempfile
import unittest
from pathlib import Path

from game.progression import ProgressionStore


class ProgressionTests(unittest.TestCase):
    def test_upgrade_consumes_core_and_increases_level(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "progression.json"
            store = ProgressionStore(path)
            store.add_core(20)

            self.assertTrue(store.try_upgrade_life())
            self.assertEqual(store.state.core_shards, 10)
            self.assertEqual(store.state.life_upgrade_level, 1)

    def test_upgrade_fails_without_core(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "progression.json"
            store = ProgressionStore(path)
            self.assertFalse(store.try_upgrade_life())
            self.assertEqual(store.state.life_upgrade_level, 0)

    def test_state_persisted(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "progression.json"
            a = ProgressionStore(path)
            a.add_core(11)
            a.try_upgrade_life()

            b = ProgressionStore(path)
            self.assertEqual(b.state.core_shards, 1)
            self.assertEqual(b.state.life_upgrade_level, 1)


if __name__ == "__main__":
    unittest.main()

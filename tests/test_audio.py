import unittest

from game.audio import stage_music_pattern


class AudioTests(unittest.TestCase):
    def test_stage_music_pattern_cycles(self):
        self.assertEqual(stage_music_pattern(1), [0, 1])
        self.assertEqual(stage_music_pattern(2), [8, 1])
        self.assertEqual(stage_music_pattern(3), [8, 9])
        self.assertEqual(stage_music_pattern(4), [10, 11])
        self.assertEqual(stage_music_pattern(5), [0, 1])


if __name__ == "__main__":
    unittest.main()

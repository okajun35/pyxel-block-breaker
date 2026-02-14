import unittest

from game.tutorial import tutorial_page, tutorial_lines


class TutorialTests(unittest.TestCase):
    def test_page_switches_every_120_frames(self):
        self.assertEqual(tutorial_page(0), 0)
        self.assertEqual(tutorial_page(119), 0)
        self.assertEqual(tutorial_page(120), 1)
        self.assertEqual(tutorial_page(240), 0)

    def test_lines_are_short(self):
        for page in (0, 1):
            lines = tutorial_lines(page)
            self.assertTrue(lines)
            self.assertTrue(all(len(line) <= 20 for line in lines))


if __name__ == "__main__":
    unittest.main()

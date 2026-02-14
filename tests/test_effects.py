import unittest

from game.effects import HitEffectSystem


class HitEffectSystemTests(unittest.TestCase):
    def test_spawn_block_hit(self):
        fx = HitEffectSystem()
        fx.spawn_block_hit(10, 20)
        self.assertEqual(len(fx.effects), 4)
        self.assertTrue(all(e.ttl > 0 for e in fx.effects))

    def test_spawn_enemy_hit_has_more_particles(self):
        fx = HitEffectSystem()
        fx.spawn_enemy_hit(10, 20, boss=False)
        normal = len(fx.effects)
        fx.effects.clear()
        fx.spawn_enemy_hit(10, 20, boss=True)
        boss = len(fx.effects)
        self.assertGreater(boss, normal)

    def test_tick_removes_expired(self):
        fx = HitEffectSystem()
        fx.spawn_block_hit(10, 20)
        for _ in range(20):
            fx.tick()
        self.assertEqual(len(fx.effects), 0)


if __name__ == "__main__":
    unittest.main()

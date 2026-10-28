"""Tests for membrane-nervous-system v0.1.0.
Run: python3 -m unittest tests -v"""
import math
import random
import unittest

from nervous import MembraneNervous, noisy, rand_field


class TestNervous(unittest.TestCase):
    def setUp(self):
        self.sys = MembraneNervous(seed=42)

    def test_stage_counts(self):
        from collections import Counter
        counts = Counter(n.stage for n in self.sys.geometry.neurons)
        self.assertEqual(counts["sensory"], 40)
        self.assertEqual(counts["spinal"], 32)
        self.assertEqual(counts["central"], 24)
        self.assertEqual(counts["motor"], 32)
        self.assertEqual(self.sys.geometry.n, 128)

    def test_four_responses(self):
        self.assertEqual(len(self.sys.patterns), 4)
        self.assertEqual(self.sys.RESPONSE_NAMES,
                         ("withdraw", "grasp", "balance", "cool-alert"))

    def test_reflex_shorter_than_central(self):
        pain = self.sys.seed_ids[0]
        self.assertLess(self.sys.reflex_time(pain),
                        self.sys.central_time(pain))

    def test_lesion_breaks_reflex_not_central(self):
        pain = self.sys.seed_ids[0]
        self.assertTrue(math.isinf(self.sys.lesion_reflex_time(pain)))
        self.assertTrue(math.isfinite(self.sys.central_time(pain)))

    def test_gate_calibrates_and_refuses(self):
        rng = random.Random(11)
        in_p = [noisy(self.sys.patterns[k % 4], 0.15, rng)
                for k in range(100)]
        ood_p = [rand_field(128, rng) for _ in range(100)]
        tau, j = self.sys.calibrate(in_p, ood_p)
        self.assertGreater(j, 0.5)
        self.assertTrue(0.0 <= tau <= 1.0)

    def test_fresh_recognition(self):
        rng = random.Random(11)
        in_p = [noisy(self.sys.patterns[k % 4], 0.15, rng)
                for k in range(100)]
        ood_p = [rand_field(128, rng) for _ in range(100)]
        self.sys.calibrate(in_p, ood_p)
        rng2 = random.Random(99)
        ok = sum(1 for k in range(40)
                 if self.sys.decide(noisy(self.sys.patterns[k % 4],
                                          0.15, rng2))[0] == "accept")
        self.assertGreaterEqual(ok, 35)

    def test_random_refused(self):
        rng = random.Random(11)
        in_p = [noisy(self.sys.patterns[k % 4], 0.15, rng)
                for k in range(100)]
        ood_p = [rand_field(128, rng) for _ in range(100)]
        self.sys.calibrate(in_p, ood_p)
        rng2 = random.Random(99)
        refused = sum(1 for _ in range(50)
                      if self.sys.decide(rand_field(128, rng2))[0]
                      == "reject")
        self.assertGreaterEqual(refused, 45)

    def test_clean_pain_is_withdraw(self):
        rng = random.Random(11)
        in_p = [noisy(self.sys.patterns[k % 4], 0.15, rng)
                for k in range(100)]
        ood_p = [rand_field(128, rng) for _ in range(100)]
        self.sys.calibrate(in_p, ood_p)
        self.assertEqual(self.sys.decide(self.sys.patterns[0])[:2],
                         ("accept", "withdraw"))


if __name__ == "__main__":
    unittest.main()

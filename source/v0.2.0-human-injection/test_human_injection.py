"""Tests for membrane-nervous-system v0.2.0 additions.
Run: python3 -m unittest test_human_injection -v
Bars are from PREREG.md, written before the demo run.
"""
import math
import random
import unittest

from human import BANDS, SENSITIVE_HZ, modulate, sensitivity
from injection import CrystallizeInjection
from nervous import MembraneNervous, noisy, rand_field


def calibrated_system():
    sys = MembraneNervous(seed=42)
    rng = random.Random(11)
    in_p = [noisy(sys.patterns[k % 4], 0.15, rng) for k in range(100)]
    ood_p = [rand_field(128, rng) for _ in range(100)]
    sys.calibrate(in_p, ood_p)
    return sys


class TestHumanFrequency(unittest.TestCase):
    def test_bands_reused(self):
        self.assertEqual(BANDS, {"breath": 0.25, "heart": 1.2,
                                 "aorta": 7.0, "brain": 10.0})
        self.assertEqual(SENSITIVE_HZ, 7.0)

    def test_sensitivity_prereg_f1(self):
        self.assertEqual(sensitivity(7.0), 1.0)
        self.assertLess(sensitivity(0.25), 0.01)
        self.assertLess(sensitivity(10.0), 0.20)

    def test_modulate_does_not_renormalise(self):
        field = [1.0 + 0j] * 4
        self.assertEqual(modulate(field, 7.0), field)
        self.assertTrue(all(abs(c) < 0.01 for c in modulate(field, 0.25)))

    def test_frequency_gate_prereg_f2(self):
        sys = calibrated_system()
        pain = sys.patterns[0]
        self.assertEqual(sys.decide(modulate(pain, 7.0))[:2],
                         ("accept", "withdraw"))
        self.assertEqual(sys.decide(modulate(pain, 0.25))[0], "reject")
        self.assertEqual(sys.decide(modulate(pain, 10.0))[0], "reject")

    def test_frequency_changes_gate_not_winner(self):
        # At 7 Hz the winner is unchanged; off-frequency only
        # lowers every overlap, so the winner (if accepted) is
        # still the same response. Check via project on the
        # unmodulated field vs the 7 Hz modulated field.
        sys = calibrated_system()
        w7, _ = sys.project(modulate(sys.patterns[0], 7.0))
        w0, _ = sys.project(sys.patterns[0])
        self.assertEqual(w7, w0)


class TestInjection(unittest.TestCase):
    def test_fail_closed_prereg_i1(self):
        sys = calibrated_system()
        inj = CrystallizeInjection(sys)
        tau_before = sys.tau
        rng = random.Random(5)
        inj.attempt(noisy(sys.patterns[0], 0.30, rng), 7.0,
                    rng=random.Random(6), truth=1)
        self.assertEqual(sys.tau, tau_before)
        self.assertEqual(len(sys.patterns), 4)

    def test_no_cost_when_accepted_prereg_i4(self):
        sys = calibrated_system()
        inj = CrystallizeInjection(sys)
        res = inj.attempt(sys.patterns[0], 7.0,
                          rng=random.Random(1), truth=1)
        self.assertEqual(res.decision, "accept")
        self.assertEqual(res.attempts, 0)

    def test_injection_needs_calibrated_gate(self):
        sys = MembraneNervous(seed=42)
        with self.assertRaises(ValueError):
            CrystallizeInjection(sys)

    def test_rescue_beats_stock_and_random_prereg_i2_i3(self):
        sys = calibrated_system()
        inj = CrystallizeInjection(sys)
        rng = random.Random(99)
        probes = [noisy(sys.patterns[k % 4], 0.30, rng)
                  for k in range(40)]
        stock = sum(1 for f in probes
                    if sys.decide(modulate(f, 7.0))[0] == "accept")
        injected = 0
        for k, f in enumerate(probes):
            res = inj.attempt(f, 7.0,
                              rng=random.Random(1000 + k), truth=1)
            if res.decision == "accept":
                injected += 1
        self.assertGreater(injected, stock)
        rng2 = random.Random(99)
        randoms = [rand_field(128, rng2) for _ in range(40)]
        rand_injected = sum(
            1 for k, f in enumerate(randoms)
            if inj.attempt(f, 7.0,
                           rng=random.Random(2000 + k),
                           truth=0).decision == "accept")
        self.assertLess(rand_injected, injected)

    def test_off_frequency_cannot_be_rescued(self):
        sys = calibrated_system()
        inj = CrystallizeInjection(sys)
        rng = random.Random(99)
        probe = noisy(sys.patterns[0], 0.30, rng)
        res = inj.attempt(probe, 0.25,
                          rng=random.Random(7), truth=1)
        self.assertEqual(res.decision, "reject")
        self.assertEqual(res.attempts, 20)


if __name__ == "__main__":
    unittest.main()

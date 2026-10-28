"""Demo for membrane-nervous-system v0.2.0.
Run: python demo_v02.py
First repeats the v0.1.0 numbers, then the frequency gate,
then the Crystallize injection rescue experiment at sigma 0.30.
Bars are from PREREG.md.
"""
import random

from human import BANDS, frequency_response, modulate, sensitivity
from injection import CrystallizeInjection
from nervous import MembraneNervous, noisy, rand_field


def main():
    sys = MembraneNervous(seed=42)
    print("membrane-nervous-system v0.2.0 — human frequency + "
          "Crystallize injection on the v0.1.0 membrane")
    print(f"bands (illustrative, from bentov-kuramoto): {BANDS}")
    print("frequency response (imposed Gaussian, centre 7.0 Hz):")
    for f, s in frequency_response([0.25, 1.2, 7.0, 10.0]):
        print(f"  {f:5.2f} Hz -> sensitivity {s:.4f}")

    rng = random.Random(11)
    in_p = [noisy(sys.patterns[k % 4], 0.15, rng) for k in range(100)]
    ood_p = [rand_field(128, rng) for _ in range(100)]
    tau, j = sys.calibrate(in_p, ood_p)
    print(f"gate calibrated (unchanged v0.1.0 method): tau = {tau:.3f}, "
          f"J = {j:.3f} (frozen)")

    pain = sys.patterns[0]
    for f in (7.0, 0.25, 10.0):
        print(f"clean pain at {f} Hz: {sys.decide(modulate(pain, f))[:2]}")

    # Rescue experiment, sigma 0.30, f = 7.0 Hz.
    inj = CrystallizeInjection(sys)
    rng = random.Random(99)
    probes = [noisy(sys.patterns[k % 4], 0.30, rng) for k in range(40)]
    stock = sum(1 for f in probes
                if sys.decide(modulate(f, 7.0))[0] == "accept")
    injected, nets = 0, []
    for k, f in enumerate(probes):
        res = inj.attempt(f, 7.0,
                          rng=random.Random(1000 + k), truth=1)
        if res.decision == "accept":
            injected += 1
        if res.net is not None:
            nets.append(res.net)
    print(f"sigma 0.30, f 7.0 Hz: stock {stock}/40 accepted, "
          f"injected {injected}/40 accepted")
    print(f"injected net score (mean over injected runs): "
          f"{sum(nets) / len(nets):.3f} "
          f"(negative means sampling did not pay for itself)")

    rng2 = random.Random(99)
    randoms = [rand_field(128, rng2) for _ in range(40)]
    rand_injected = 0
    for k, f in enumerate(randoms):
        res = inj.attempt(f, 7.0,
                          rng=random.Random(2000 + k), truth=0)
        if res.decision == "accept":
            rand_injected += 1
    print(f"random fields, injected: {rand_injected}/40 accepted "
          f"(must stay below the noisy injected rate)")
    print(f"tau after injection: {sys.tau:.3f} (unchanged), "
          f"patterns stored: {len(sys.patterns)} (still 4)")


if __name__ == "__main__":
    main()

"""Demo for membrane-nervous-system v0.1.0. Run: python demo.py"""
import random

from nervous import MembraneNervous, noisy, rand_field


def main():
    sys = MembraneNervous(seed=42)
    geo = sys.geometry
    from collections import Counter
    counts = Counter(n.stage for n in geo.neurons)
    print(f"membrane-nervous-system v0.1.0 — {geo.n} neurons "
          f"({dict(counts)}), {len(geo.edges)} edges, "
          f"{len(geo.cross_stage_edges)} cross-stage, "
          f"{len(geo.reflex_edges)} reflex")
    pain = sys.seed_ids[0]
    print(f"pain seed {pain}: reflex median "
          f"{sys.reflex_time(pain):.2f} distance units, central median "
          f"{sys.central_time(pain):.2f} distance units")
    print(f"lesion (reflex edges cut, central excluded): "
          f"{sys.lesion_reflex_time(pain)} "
          f"(inf = motor unreachable on the reflex route)")

    rng = random.Random(11)
    in_probes = [noisy(sys.patterns[k % 4], 0.15, rng)
                 for k in range(100)]
    ood_probes = [rand_field(128, rng) for _ in range(100)]
    tau, j = sys.calibrate(in_probes, ood_probes)
    print(f"gate calibrated: tau = {tau:.3f}, Youden J = {j:.3f} (frozen)")

    rng2 = random.Random(99)
    ok = sum(1 for k in range(40)
             if sys.decide(noisy(sys.patterns[k % 4], 0.15, rng2))[0]
             == "accept")
    refused = sum(1 for _ in range(50)
                  if sys.decide(rand_field(128, rng2))[0] == "reject")
    print(f"fresh noisy recognition: {ok}/40")
    print(f"fresh random fields refused: {refused}/50")
    print(f"clean pain probe: {sys.decide(sys.patterns[0])[:2]}")


if __name__ == "__main__":
    main()

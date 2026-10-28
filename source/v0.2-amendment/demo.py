"""Fixed-seed illustration only; the frozen-protocol benchmark is benchmark.py."""
import random

from nervous_v2 import (
    RESPONSE_BY_MODALITY,
    SyntheticMembrane,
    calibrate_threshold,
    decide,
    noisy,
    random_field,
)


def main():
    print("SYNTHETIC TOY, NOT PHYSIOLOGY.")
    print("Fixed-seed illustration only; all fields and labels are synthetic.")
    model = SyntheticMembrane(seed=42)
    by_modality = model.geometry.sensory_by_modality()
    templates = {}
    for modality, response in RESPONSE_BY_MODALITY.items():
        templates[response] = model.wave(by_modality[modality][0])

    rng_cal = random.Random(11)
    in_cal = [
        noisy(templates[response], 0.15, rng_cal)
        for i, response in enumerate(RESPONSE_BY_MODALITY.values())
        for _ in range(25)
    ]
    ood_cal = [random_field(model.geometry.n, rng_cal) for _ in range(100)]
    tau, j = calibrate_threshold(in_cal, ood_cal, templates)
    print("Calibration (used to select the threshold):")
    print(f"  in-domain noisy probes: {len(in_cal)}")
    print(f"  random-field OOD probes: {len(ood_cal)}")
    print(f"  frozen threshold: {tau:.3f}; calibration Youden J: {j:.3f}")

    rng_test = random.Random(99)
    fresh_in = [
        (response, noisy(templates[response], 0.15, rng_test))
        for i, response in enumerate(RESPONSE_BY_MODALITY.values())
        for _ in range(10)
    ]
    accepted = 0
    correct = 0
    correctly_accepted = 0
    for expected, field in fresh_in:
        status, predicted, _, _ = decide(field, templates, tau)
        accepted += status == "accept"
        correct += predicted == expected
        correctly_accepted += status == "accept" and predicted == expected
    fresh_ood = [random_field(model.geometry.n, rng_test) for _ in range(50)]
    rejected = sum(decide(field, templates, tau)[0] == "reject"
                   for field in fresh_ood)
    print("Fresh checks (not used to select the threshold):")
    print(f"  noisy in-domain accepted: {accepted}/{len(fresh_in)}")
    print(f"  noisy in-domain expected labels correct: {correct}/{len(fresh_in)}")
    print(f"  correctly labelled and accepted: {correctly_accepted}/{len(fresh_in)}")
    print(f"  random-field OOD rejected: {rejected}/{len(fresh_ood)}")
    pain_source = by_modality["pain"][0]
    reflex = model.route_median(
        pain_source, ("sensory", "spinal", "motor"))
    central = model.route_median(
        pain_source, ("sensory", "spinal", "central", "motor"))
    print("Geometry-only route distances for the first pain-labelled node:")
    print(f"  ordered reflex route: {reflex:.2f} arbitrary units")
    print(f"  ordered central route: {central:.2f} arbitrary units")


if __name__ == "__main__":
    main()

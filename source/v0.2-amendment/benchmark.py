"""Run the frozen local synthetic benchmark described in PROTOCOL.md."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

from nervous_v2 import (
    RESPONSE_BY_MODALITY,
    SyntheticMembrane,
    calibrate_threshold,
    decide,
    noisy,
    normalize,
    random_field,
)

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
N_SEEDS = 100
SIGMAS = (0.05, 0.15, 0.30)
REPLICATES = 5
BOOTSTRAPS = 2000
MODEL_NAMES = ("centroid", "single_exemplar")
ROUTES = {
    "reflex": ("sensory", "spinal", "motor"),
    "central": ("sensory", "spinal", "central", "motor"),
}


def mean(values):
    return statistics.mean(values) if values else math.nan


def cluster_interval(values, rng):
    """Mean and percentile interval, resampling geometry seeds as clusters."""
    if not values:
        return {"mean": None, "ci95_low": None, "ci95_high": None}
    boot = []
    n = len(values)
    for _ in range(BOOTSTRAPS):
        boot.append(mean([values[rng.randrange(n)] for _ in range(n)]))
    boot.sort()
    lo = boot[int(0.025 * (BOOTSTRAPS - 1))]
    hi = boot[int(0.975 * (BOOTSTRAPS - 1))]
    return {"mean": mean(values), "ci95_low": lo, "ci95_high": hi}


def build_templates(model, waves, train_ids):
    centroid = {}
    single = {}
    for modality, source_ids in train_ids.items():
        label = RESPONSE_BY_MODALITY[modality]
        vectors = [waves[source] for source in source_ids]
        if not vectors:
            raise ValueError("each class requires at least one training source")
        centroid[label] = normalize([
            sum(vector[index] for vector in vectors) / len(vectors)
            for index in range(model.geometry.n)
        ])
        single[label] = list(vectors[0])
    return {"centroid": centroid, "single_exemplar": single}


def mixtures(templates, count, rng):
    labels = sorted(templates)
    output = []
    for _ in range(count):
        left, right = rng.sample(labels, 2)
        output.append(normalize([
            a + b for a, b in zip(templates[left], templates[right])
        ]))
    return output


def class_metrics(records):
    labels = tuple(RESPONSE_BY_MODALITY.values())
    by_label = {label: [r for r in records if r["truth"] == label]
                for label in labels}
    raw = []
    coverage = []
    selective = []
    for label in labels:
        group = by_label[label]
        if not group:
            raise ValueError(f"missing held-out probes for {label}")
        raw.append(sum(r["prediction"] == label for r in group) / len(group))
        coverage.append(sum(r["accepted"] for r in group) / len(group))
        accepted = [r for r in group if r["accepted"]]
        selective.append(
            sum(r["prediction"] == label for r in accepted) / len(accepted)
            if accepted else 0.0
        )
    return {
        "macro_accuracy_before_rejection": mean(raw),
        "macro_acceptance_coverage": mean(coverage),
        "macro_accuracy_among_accepted": mean(selective),
    }


def evaluate_model(fields, templates, threshold):
    records = []
    for truth, sigma, field in fields:
        status, prediction, score, _ = decide(field, templates, threshold)
        records.append({
            "truth": truth,
            "sigma": sigma,
            "prediction": prediction,
            "accepted": status == "accept",
            "score": score,
        })
    return records


def make_in_fields(waves, test_ids, rng):
    fields = []
    for modality, source_ids in test_ids.items():
        truth = RESPONSE_BY_MODALITY[modality]
        for source in source_ids:
            for sigma in SIGMAS:
                for _ in range(REPLICATES):
                    fields.append((truth, sigma,
                                   noisy(waves[source], sigma, rng)))
    return fields


def summarise_records(records, row, metric_values, model_name):
    scopes = [(f"sigma_{sigma:.2f}",
               [record for record in records if record["sigma"] == sigma])
              for sigma in SIGMAS]
    scopes.append(("pooled", records))
    output = {}
    for scope, selected in scopes:
        metrics = class_metrics(selected)
        output[scope] = metrics
        for metric, value in metrics.items():
            key = f"{model_name}.in_domain.{scope}.{metric}"
            metric_values[key].append(value)
            row[key] = value
    return output


def run_geometry(seed, aggregate_values):
    model = SyntheticMembrane(seed=seed)
    geometry = model.geometry
    waves = {source: model.wave(source) for source in range(geometry.n)}
    all_by_modality = geometry.sensory_by_modality()
    train_ids = {}
    test_ids = {}
    for modality, source_ids in all_by_modality.items():
        sorted_ids = sorted(source_ids)
        split = len(sorted_ids) // 2
        train_ids[modality] = sorted_ids[:split]
        test_ids[modality] = sorted_ids[split:]

    templates_by_model = build_templates(model, waves, train_ids)
    calibration_rng = random.Random(100_000 + seed)
    calibration_in = [
        noisy(waves[source], 0.15, calibration_rng)
        for ids in train_ids.values()
        for source in ids
        for _ in range(REPLICATES)
    ]
    calibration_random = [
        random_field(geometry.n, calibration_rng) for _ in range(20)
    ]
    row = {"seed": seed,
           "training_sources": sum(map(len, train_ids.values())),
           "heldout_sources": sum(map(len, test_ids.values()))}
    thresholds = {}
    calibration_mixtures = mixtures(
        templates_by_model["centroid"], 20, calibration_rng)
    calibration_ood = calibration_random + calibration_mixtures
    calibration_ood_count = len(calibration_ood)
    for model_name, templates in templates_by_model.items():
        threshold, calibration_j = calibrate_threshold(
            calibration_in, calibration_ood, templates)
        thresholds[model_name] = threshold
        row[f"{model_name}.tau"] = threshold
        row[f"{model_name}.calibration_youden_j"] = calibration_j
        aggregate_values[f"{model_name}.calibration.tau"].append(threshold)
        aggregate_values[f"{model_name}.calibration.youden_j"].append(
            calibration_j)

    test_rng = random.Random(200_000 + seed)
    in_fields = make_in_fields(waves, test_ids, test_rng)
    records_by_model = {}
    for model_name, templates in templates_by_model.items():
        records = evaluate_model(in_fields, templates, thresholds[model_name])
        records_by_model[model_name] = records
        summarise_records(records, row, aggregate_values, model_name)

    # Fresh OOD checks: two calibration families plus unseen source stages.
    ood_families = {
        "random_field": [random_field(geometry.n, test_rng) for _ in range(20)],
    }
    # Use the centroid prototypes for both models' mixture family generation;
    # each family's test draws are independent of calibration draws.
    ood_families["class_mixture"] = mixtures(
        templates_by_model["centroid"], 20, test_rng)
    stage_fields = []
    for stage in ("spinal", "central", "motor"):
        stage_fields.extend(waves[source] for source in geometry.ids(stage))
    ood_families["non_sensory_source_wave"] = stage_fields
    for model_name, templates in templates_by_model.items():
        pooled = []
        for family, fields in ood_families.items():
            rejected = sum(decide(field, templates, thresholds[model_name])[0]
                           == "reject" for field in fields)
            rate = rejected / len(fields)
            row[f"{model_name}.ood.{family}.rejection_rate"] = rate
            aggregate_values[
                f"{model_name}.ood.{family}.rejection_rate"].append(rate)
            pooled.extend(fields)
        pooled_rate = sum(
            decide(field, templates, thresholds[model_name])[0] == "reject"
            for field in pooled
        ) / len(pooled)
        row[f"{model_name}.ood.pooled.rejection_rate"] = pooled_rate
        aggregate_values[f"{model_name}.ood.pooled.rejection_rate"].append(
            pooled_rate)

    sensory_sources = geometry.ids("sensory")
    route_source_medians = {name: [] for name in ROUTES}
    for source in sensory_sources:
        for name, route in ROUTES.items():
            distances = geometry.ordered_route_distances(source, route)
            finite = [value for value in distances.values()
                      if math.isfinite(value)]
            route_source_medians[name].append(_median(finite))
    reflex = _median(route_source_medians["reflex"])
    central = _median(route_source_medians["central"])
    row["route.reflex_median_distance"] = reflex
    row["route.central_median_distance"] = central
    row["route.reflex_minus_central"] = reflex - central
    row["route.reflex_shorter"] = float(reflex < central)
    for key in ("route.reflex_median_distance", "route.central_median_distance",
                "route.reflex_minus_central", "route.reflex_shorter"):
        aggregate_values[key].append(row[key])

    lesion_ok = True
    for source in sensory_sources:
        lesioned_reflex = model.route_median(
            source, ROUTES["reflex"], removed_edges=geometry.reflex_edges)
        surviving_central = model.route_median(
            source, ROUTES["central"], removed_edges=geometry.reflex_edges)
        lesion_ok &= math.isinf(lesioned_reflex) and math.isfinite(surviving_central)
    row["lesion.all_sensory_sources_pass"] = float(lesion_ok)
    aggregate_values["lesion.all_sensory_sources_pass"].append(float(lesion_ok))
    row["calibration.in_domain_count"] = len(calibration_in)
    row["calibration.ood_count"] = calibration_ood_count
    row["test.in_domain_count"] = len(in_fields)
    row["test.ood_count"] = sum(len(fields) for fields in ood_families.values())
    return row


def _median(values):
    values = sorted(values)
    if not values:
        return math.inf
    m = len(values) // 2
    return values[m] if len(values) % 2 else (values[m - 1] + values[m]) / 2.0


def main():
    protocol_path = ROOT / "PROTOCOL.md"
    freeze_path = ROOT / "PROTOCOL_FREEZE.txt"
    protocol_hash = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
    frozen_text = freeze_path.read_text(encoding="utf-8")
    if f"SHA-256: {protocol_hash}" not in frozen_text:
        raise RuntimeError("PROTOCOL.md changed after its recorded freeze")

    print("SYNTHETIC TOY, NOT PHYSIOLOGY — all benchmark fields are generated.")
    aggregate_values = defaultdict(list)
    rows = []
    for seed in range(N_SEEDS):
        rows.append(run_geometry(seed, aggregate_values))
        if (seed + 1) % 10 == 0:
            print(f"Completed {seed + 1}/{N_SEEDS} geometry seeds.")
    if not all(row["lesion.all_sensory_sources_pass"] == 1.0 for row in rows):
        raise RuntimeError("stage-ordered lesion invariant failed")

    # Fixed-seed percentile cluster bootstrap, with a stable metric order.
    ci_rng = random.Random(999)
    summaries = {
        key: cluster_interval(aggregate_values[key], ci_rng)
        for key in sorted(aggregate_values)
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    script_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    output = {
        "title": "Local synthetic v0.2 benchmark; not physiology",
        "protocol_sha256": protocol_hash,
        "benchmark_script_sha256": script_hash,
        "geometry_seeds": N_SEEDS,
        "heldout_sigmas": list(SIGMAS),
        "heldout_replicates_per_source_sigma": REPLICATES,
        "bootstrap_replicates": BOOTSTRAPS,
        "bootstrap_seed": 999,
        "random_choice_balanced_accuracy_reference": 0.25,
        "counts": {
            "calibration_in_domain_total": sum(
                row["calibration.in_domain_count"] for row in rows),
            "calibration_ood_total": sum(
                row["calibration.ood_count"] for row in rows),
            "heldout_in_domain_total": sum(
                row["test.in_domain_count"] for row in rows),
            "heldout_ood_total": sum(
                row["test.ood_count"] for row in rows),
        },
        "summaries_seed_cluster_bootstrap_95_percentile_ci": summaries,
        "per_seed": rows,
    }
    json_path = RESULTS / "results.json"
    json_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n",
                         encoding="utf-8")
    csv_path = RESULTS / "per_seed.csv"
    columns = sorted({column for row in rows for column in row})
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    print("Calibration data (threshold selection only):")
    print(f"  in-domain probes: {output['counts']['calibration_in_domain_total']}")
    print(f"  OOD probes: {output['counts']['calibration_ood_total']}")
    print("Fresh held-out evaluation (not used to select thresholds):")
    print(f"  in-domain probes: {output['counts']['heldout_in_domain_total']}")
    print(f"  OOD probes: {output['counts']['heldout_ood_total']}")
    for model_name in MODEL_NAMES:
        key = f"{model_name}.in_domain.pooled.macro_accuracy_before_rejection"
        item = summaries[key]
        print(f"  {model_name} macro label accuracy: {item['mean']:.3f} "
              f"(seed-clustered 95% CI {item['ci95_low']:.3f}–"
              f"{item['ci95_high']:.3f})")
    print(f"Wrote {json_path} and {csv_path}")


if __name__ == "__main__":
    main()

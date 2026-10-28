"""Route-only recomputation for amendment 1; does not run classifiers."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import statistics
from pathlib import Path

from nervous_v2 import SyntheticMembrane
from route_coverage import summarize_layout, summarize_target_distances

ROOT = Path(__file__).resolve().parent
SEEDS = range(100)
ROUTES = {
    "reflex": ("sensory", "spinal", "motor"),
    "central": ("sensory", "spinal", "central", "motor"),
}
EXPECTED_HASHES = {
    "original_protocol": "83f50f7744fd5f980cfc66b41d3d2c0bd41c7af8a7245dd1a855b30e3636037c",
    "original_results": "e030007712cadd9c9ff6903d075f1930872b1d11022c8df8aea32794124114b2",
    "original_per_seed": "3fc0eb817fa89fda5f90ed510d82912315f9f43c1f28d3a8f8b42cffb2e1b1cb",
    "original_zip": "0527b90943b10a082682620df3bb1d69d696e86dfede0e0def49a610ea6892bb",
}
BOOTSTRAPS = 2000


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bootstrap_mean_ci(values, rng):
    if not values:
        return {"mean": None, "ci95_low": None, "ci95_high": None}
    n = len(values)
    boot = [statistics.mean(values[rng.randrange(n)] for _ in range(n))
            for _ in range(BOOTSTRAPS)]
    boot.sort()
    return {
        "mean": statistics.mean(values),
        "ci95_low": boot[int(0.025 * (BOOTSTRAPS - 1))],
        "ci95_high": boot[int(0.975 * (BOOTSTRAPS - 1))],
    }


def main():
    base_results_path = ROOT / "results/results.json"
    base_csv_path = ROOT / "results/per_seed.csv"
    zip_candidates = (
        ROOT.parent / "membrane-nervous-system-v0.2.0-local.zip",
        ROOT / "first_record/membrane-nervous-system-v0.2.0-local.zip",
    )
    zip_path = next((path for path in zip_candidates if path.is_file()), None)
    if zip_path is None:
        raise FileNotFoundError("first v0.2.0 ZIP required for hash verification")
    amendment_path = ROOT / "PROTOCOL_AMENDMENT_2026-10-27.md"
    amendment_freeze_path = ROOT / "PROTOCOL_AMENDMENT_FREEZE_2026-10-27.txt"
    freeze_text = amendment_freeze_path.read_text(encoding="utf-8")
    amendment_hash = sha(amendment_path)
    if f"SHA-256: {amendment_hash}" not in freeze_text:
        raise RuntimeError("route amendment changed after its freeze")
    observed = {
        "original_protocol": sha(ROOT / "PROTOCOL.md"),
        "original_results": sha(base_results_path),
        "original_per_seed": sha(base_csv_path),
        "original_zip": sha(zip_path),
    }
    if observed != EXPECTED_HASHES:
        raise RuntimeError(f"first v0.2 record hash mismatch: {observed}")
    baseline = json.loads(base_results_path.read_text(encoding="utf-8"))
    prior_per_seed = {row["seed"]: row for row in baseline["per_seed"]}
    if set(prior_per_seed) != set(SEEDS):
        raise RuntimeError("baseline does not contain exactly geometry seeds 0–99")

    rows = []
    layout_rows = []
    for seed in SEEDS:
        system = SyntheticMembrane(seed=seed)
        geometry = system.geometry
        sensory_ids = geometry.ids("sensory")
        layout_route_rows = {}
        for route_name, stage_order in ROUTES.items():
            source_summaries = []
            source_conditional_medians = []
            for source in sensory_ids:
                node = geometry.nodes[source]
                all_target_distances = geometry.ordered_route_distances(
                    source, stage_order
                )
                if len(all_target_distances) != 32:
                    raise RuntimeError(
                        f"seed {seed} {route_name}: expected 32 motor targets"
                    )
                summary = summarize_target_distances(all_target_distances)
                source_summaries.append(summary)
                median_distance = summary[
                    "median_distance_among_reachable_targets"
                ]
                if median_distance is not None:
                    source_conditional_medians.append(median_distance)
                rows.append({
                    "geometry_seed": seed,
                    "source_id": source,
                    "source_modality": node.modality or "unlabeled_sensory",
                    "route": route_name,
                    **summary,
                })
            layout_summary = summarize_layout(source_summaries)
            layout_route_rows[route_name] = {
                **layout_summary,
                "median_of_source_medians_among_reachable_targets": (
                    statistics.median(source_conditional_medians)
                    if source_conditional_medians else None
                ),
            }
            layout_rows.append({
                "geometry_seed": seed,
                "route": route_name,
                **layout_route_rows[route_name],
            })

        # Confirm the recomputation uses the exact deterministic layouts and
        # reproduces the first-record conditional distance summaries.
        prior = prior_per_seed[seed]
        for route_name in ROUTES:
            key = f"route.{route_name}_median_distance"
            recalculated = layout_route_rows[route_name][
                "median_of_source_medians_among_reachable_targets"
            ]
            if recalculated is None or not math.isclose(
                    recalculated, prior[key], rel_tol=0.0, abs_tol=1e-12):
                raise RuntimeError(
                    f"seed {seed} {route_name} distance does not match first record"
                )

    # Summaries are cluster-level (geometry seed), never probe-level.
    by_route = {}
    for route_name in ROUTES:
        src_rows = [row for row in rows if row["route"] == route_name]
        lay_rows = [row for row in layout_rows if row["route"] == route_name]
        coverage_values = [row["target_coverage"] for row in src_rows]
        layout_coverages = [row["target_coverage"] for row in lay_rows]
        distance_values = [
            row["median_of_source_medians_among_reachable_targets"]
            for row in lay_rows
            if row["median_of_source_medians_among_reachable_targets"] is not None
        ]
        by_route[route_name] = {
            "source_layout_pairs": len(src_rows),
            "motor_targets_per_source": 32,
            "total_source_target_opportunities": sum(
                row["total_motor_targets"] for row in src_rows
            ),
            "reachable_source_target_pairs": sum(
                row["reachable_targets"] for row in src_rows
            ),
            "unreachable_source_target_pairs": sum(
                row["unreachable_targets"] for row in src_rows
            ),
            "mean_source_layout_target_coverage": statistics.mean(coverage_values),
            "minimum_source_layout_target_coverage": min(coverage_values),
            "maximum_source_layout_target_coverage": max(coverage_values),
            "layout_target_coverage_mean_cluster_bootstrap_95_ci": None,
            "distance_summary_name": (
                "mean of layout medians of source medians among reachable targets"
            ),
            "distance_summary_mean_cluster_bootstrap_95_ci": None,
            "layout_median_distance_min": min(distance_values),
            "layout_median_distance_max": max(distance_values),
            "layouts_with_all_source_medians_defined": len(distance_values),
        }

    # Use the frozen seed-999, 2,000-resample geometry-cluster rule.
    rng = random.Random(999)
    for route_name in ROUTES:
        lay_rows = [row for row in layout_rows if row["route"] == route_name]
        by_route[route_name]["layout_target_coverage_mean_cluster_bootstrap_95_ci"] = (
            bootstrap_mean_ci([row["target_coverage"] for row in lay_rows], rng)
        )
        distances = [
            row["median_of_source_medians_among_reachable_targets"]
            for row in lay_rows
            if row["median_of_source_medians_among_reachable_targets"] is not None
        ]
        by_route[route_name]["distance_summary_mean_cluster_bootstrap_95_ci"] = (
            bootstrap_mean_ci(distances, rng)
        )

    reflex = [row for row in layout_rows if row["route"] == "reflex"]
    central = [row for row in layout_rows if row["route"] == "central"]
    reflex_by_seed = {row["geometry_seed"]: row for row in reflex}
    central_by_seed = {row["geometry_seed"]: row for row in central}
    diffs = [
        reflex_by_seed[seed]["median_of_source_medians_among_reachable_targets"]
        - central_by_seed[seed]["median_of_source_medians_among_reachable_targets"]
        for seed in SEEDS
    ]
    shorter_fraction = sum(value < 0 for value in diffs) / len(diffs)
    by_route["conditional_distance_comparison"] = {
        "reflex_minus_central_layout_distance_mean_cluster_bootstrap_95_ci":
            bootstrap_mean_ci(diffs, rng),
        "fraction_layouts_reflex_conditional_median_shorter": shorter_fraction,
        "interpretation": (
            "Not interpretable as a full route-order comparison without coverage; "
            "these are conditional medians among reachable targets."
        ),
    }

    route_results = {
        "title": "Amended route reachability and conditional-distance results",
        "date": "2026-10-27",
        "scope": "route-only deterministic recalculation; no classifier rerun",
        "original_frozen_protocol_sha256": EXPECTED_HASHES["original_protocol"],
        "amendment_sha256": amendment_hash,
        "original_results_json_sha256": EXPECTED_HASHES["original_results"],
        "original_per_seed_csv_sha256": EXPECTED_HASHES["original_per_seed"],
        "original_v0_2_zip_sha256": EXPECTED_HASHES["original_zip"],
        "nervous_v2_source_sha256": sha(ROOT / "nervous_v2.py"),
        "geometry_seeds": list(SEEDS),
        "sensory_sources_per_layout": 40,
        "motor_targets_per_source": 32,
        "route_summaries": by_route,
        "files": {
            "per_source_layout": "route_coverage_by_source_layout_2026-10-27.csv",
            "per_layout": "route_coverage_by_layout_2026-10-27.csv",
            "distance_semantics": "median among reachable motor targets only",
            "coverage_semantics": "all 32 motor targets remain in every denominator",
        },
        "no_new_classifier_probes_or_randomized_model_data": True,
    }
    out_json = ROOT / "results/route_coverage_amendment_2026-10-27.json"
    out_source = ROOT / "results/route_coverage_by_source_layout_2026-10-27.csv"
    out_layout = ROOT / "results/route_coverage_by_layout_2026-10-27.csv"
    out_json.write_text(json.dumps(route_results, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    for path, data in ((out_source, rows), (out_layout, layout_rows)):
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(data[0]))
            writer.writeheader()
            writer.writerows(data)

    print("Route-only deterministic recalculation complete.")
    for route_name in ROUTES:
        result = by_route[route_name]
        print(
            f"{route_name}: mean source-layout coverage="
            f"{result['mean_source_layout_target_coverage']:.6%}, "
            f"min={result['minimum_source_layout_target_coverage']:.6%}, "
            f"max={result['maximum_source_layout_target_coverage']:.6%}; "
            f"conditional layout-median distance mean="
            f"{result['distance_summary_mean_cluster_bootstrap_95_ci']['mean']:.4f}"
        )
    print("Wrote", out_json)
    print("Wrote", out_source)
    print("Wrote", out_layout)


if __name__ == "__main__":
    main()

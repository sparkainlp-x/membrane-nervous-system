"""Tests for the dated route-coverage amendment."""
import csv
import math
import unittest
from pathlib import Path

from nervous_v2 import SyntheticMembrane
from route_coverage import summarize_layout, summarize_target_distances


class TestRouteCoverageAmendment(unittest.TestCase):
    def test_infinity_is_counted_not_silently_dropped(self):
        summary = summarize_target_distances({
            0: 1.0,
            1: math.inf,
            2: 3.0,
            3: math.inf,
        })
        self.assertEqual(summary["total_motor_targets"], 4)
        self.assertEqual(summary["reachable_targets"], 2)
        self.assertEqual(summary["unreachable_targets"], 2)
        self.assertEqual(summary["target_coverage"], 0.5)
        self.assertEqual(summary["median_distance_among_reachable_targets"], 2.0)

    def test_all_unreachable_has_zero_coverage_and_no_distance_median(self):
        summary = summarize_target_distances({0: math.inf, 1: math.inf})
        self.assertEqual(summary["total_motor_targets"], 2)
        self.assertEqual(summary["reachable_targets"], 0)
        self.assertEqual(summary["unreachable_targets"], 2)
        self.assertEqual(summary["target_coverage"], 0.0)
        self.assertIsNone(summary["median_distance_among_reachable_targets"])

    def test_layout_coverage_uses_all_targets_and_reports_source_coverage(self):
        one_of_two = summarize_target_distances({0: 2.0, 1: math.inf})
        zero_of_two = summarize_target_distances({0: math.inf, 1: math.inf})
        layout = summarize_layout([one_of_two, zero_of_two])
        self.assertEqual(layout["source_target_opportunities"], 4)
        self.assertEqual(layout["reachable_source_target_pairs"], 1)
        self.assertEqual(layout["unreachable_source_target_pairs"], 3)
        self.assertEqual(layout["target_coverage"], 0.25)
        self.assertEqual(layout["min_source_target_coverage"], 0.0)
        self.assertEqual(layout["max_source_target_coverage"], 0.5)
        self.assertEqual(layout["sources_with_no_reachable_motor_targets"], 1)
        self.assertEqual(layout["source_rows_with_reachable_motor_targets"], 1)
        self.assertEqual(
            layout["median_of_source_medians_among_reachable_targets"], 2.0
        )

    def test_actual_seed_2_central_route_retains_27_unreachable_targets(self):
        geometry = SyntheticMembrane(seed=2).geometry
        source = 0  # first sensory node, touch-labelled in the frozen layout
        distances = geometry.ordered_route_distances(
            source, ("sensory", "spinal", "central", "motor")
        )
        summary = summarize_target_distances(distances)
        self.assertEqual(len(distances), 32)
        self.assertTrue(any(math.isinf(value) for value in distances.values()))
        self.assertEqual(summary["reachable_targets"], 5)
        self.assertEqual(summary["unreachable_targets"], 27)
        self.assertEqual(summary["target_coverage"], 5 / 32)
        self.assertIsNotNone(
            summary["median_distance_among_reachable_targets"]
        )

    def test_amended_csv_reports_all_route_source_pairs_and_known_case(self):
        path = (Path(__file__).parent / "results"
                / "route_coverage_by_source_layout_2026-10-27.csv")
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 8000)  # 100 layouts × 40 sources × 2 routes
        selected = [row for row in rows
                    if row["geometry_seed"] == "2"
                    and row["source_id"] == "0"
                    and row["route"] == "central"]
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["total_motor_targets"], "32")
        self.assertEqual(selected[0]["reachable_targets"], "5")
        self.assertEqual(selected[0]["unreachable_targets"], "27")
        self.assertAlmostEqual(float(selected[0]["target_coverage"]), 5 / 32)

    def test_empty_or_nan_distance_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            summarize_target_distances({})
        with self.assertRaises(ValueError):
            summarize_target_distances({0: math.nan})


if __name__ == "__main__":
    unittest.main()

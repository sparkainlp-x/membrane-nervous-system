"""Regression tests for the separate synthetic v0.2 implementation."""
import math
import random
import unittest

from nervous_v2 import (
    RESPONSE_BY_MODALITY,
    SyntheticMembrane,
    calibrate_threshold,
    decide,
    median,
    noisy,
    normalize,
    overlap,
    random_field,
)


class TestV2(unittest.TestCase):
    def setUp(self):
        self.model = SyntheticMembrane(seed=42)
        self.geo = self.model.geometry

    def test_fixed_stage_sizes_and_reproducibility(self):
        other = SyntheticMembrane(seed=42)
        self.assertEqual(self.geo.n, 128)
        self.assertEqual([n.x for n in self.geo.nodes],
                         [n.x for n in other.geometry.nodes])
        self.assertEqual(self.geo.edges, other.geometry.edges)

    def test_cross_stage_edges_only_follow_forward_transitions(self):
        allowed = {
            ("sensory", "spinal"),
            ("spinal", "motor"),
            ("spinal", "central"),
            ("central", "motor"),
        }
        cross = [(a, b) for a, b in self.geo.edges
                 if self.geo.nodes[a].stage != self.geo.nodes[b].stage]
        self.assertTrue(cross)
        self.assertTrue(all((self.geo.nodes[a].stage,
                             self.geo.nodes[b].stage) in allowed
                            for a, b in cross))
        self.assertTrue(all((b, a) not in self.geo.edges for a, b in cross))

    def test_constrained_routes_and_lesion_control(self):
        source = self.geo.sensory_by_modality()["pain"][0]
        reflex = self.model.route_median(source,
                                         ("sensory", "spinal", "motor"))
        central = self.model.route_median(
            source, ("sensory", "spinal", "central", "motor"))
        lesioned = self.model.route_median(
            source, ("sensory", "spinal", "motor"),
            removed_edges=self.geo.reflex_edges)
        self.assertTrue(math.isfinite(reflex))
        self.assertTrue(math.isfinite(central))
        self.assertTrue(math.isinf(lesioned))
        # The unchanged central path remains available after the reflex cut.
        central_after = self.model.route_median(
            source, ("sensory", "spinal", "central", "motor"),
            removed_edges=self.geo.reflex_edges)
        self.assertTrue(math.isfinite(central_after))

    def test_all_sensory_sources_have_stage_ordered_routes(self):
        for source in self.geo.ids("sensory"):
            self.assertTrue(math.isfinite(self.model.route_median(
                source, ("sensory", "spinal", "motor"))))
            self.assertTrue(math.isfinite(self.model.route_median(
                source, ("sensory", "spinal", "central", "motor"))))

    def test_median_uses_average_for_even_counts(self):
        self.assertEqual(median([1, 2]), 1.5)
        self.assertEqual(median([3, 1, 2]), 2)
        self.assertTrue(math.isinf(median([])))

    def test_overlap_rejects_wrong_vector_dimensions(self):
        with self.assertRaises(ValueError):
            overlap([1 + 0j], [1 + 0j, 0j])

    def test_noise_and_random_field_validation(self):
        with self.assertRaises(ValueError):
            normalize([0j, 0j])
        with self.assertRaises(ValueError):
            noisy([1 + 0j], -0.1, random.Random(1))
        with self.assertRaises(ValueError):
            random_field(0, random.Random(1))

    def test_calibration_rejects_empty_or_invalid_inputs(self):
        templates = {"a": self.model.wave(0)}
        with self.assertRaises(ValueError):
            calibrate_threshold([], [templates["a"]], templates)
        with self.assertRaises(ValueError):
            calibrate_threshold([templates["a"]], [], templates)
        with self.assertRaises(ValueError):
            calibrate_threshold([templates["a"]], [templates["a"]],
                                templates, grid_step=0)

    def test_exact_training_source_waves_recover_expected_labels(self):
        sensory = self.geo.sensory_by_modality()
        templates = {}
        expected = {}
        for modality, response in RESPONSE_BY_MODALITY.items():
            source = sensory[modality][0]
            templates[response] = self.model.wave(source)
            expected[source] = response
        for source, response in expected.items():
            result = decide(self.model.wave(source), templates, 0.0)
            self.assertEqual(result[0], "accept")
            self.assertEqual(result[1], response)

    def test_noisy_probe_preserves_field_norm(self):
        field = self.model.wave(self.geo.ids("sensory")[0])
        observed = noisy(field, 0.15, random.Random(99))
        self.assertAlmostEqual(sum(abs(x) ** 2 for x in observed), 1.0,
                               places=12)


if __name__ == "__main__":
    unittest.main()

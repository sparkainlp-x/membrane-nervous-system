"""membrane-nervous-system v0.2.0: an explicitly synthetic graph toy.

This module is not a model of human physiology. Its directed graph and
stage-ordered routes are software definitions, not neural mechanisms.
"""
from __future__ import annotations

import heapq
import math
import random
from collections import defaultdict

VERSION = "0.2.0"
STAGE_ORDER = ("sensory", "spinal", "central", "motor")
MODALITIES = ("touch", "temperature", "pain", "proprioception")
RESPONSE_BY_MODALITY = {
    "pain": "withdraw",
    "touch": "grasp",
    "proprioception": "balance",
    "temperature": "cool-alert",
}
# stage, count, ellipse centre x/y, radii x/y, node labels
STAGE_SPECS = (
    ("sensory", 40, -24.0, 0.0, 7.0, 28.0,
     ["touch"] * 12 + ["temperature"] * 8 + ["pain"] * 8
     + ["proprioception"] * 12),
    ("spinal", 32, 0.0, 0.0, 7.0, 28.0, [None] * 32),
    ("central", 24, 0.0, 38.0, 18.0, 8.0, [None] * 24),
    ("motor", 32, 24.0, 0.0, 7.0, 28.0, [None] * 32),
)


def normalize(vector):
    norm = math.sqrt(sum(abs(value) ** 2 for value in vector))
    if norm == 0.0:
        raise ValueError("cannot normalize a zero vector")
    return [value / norm for value in vector]


def overlap(field, pattern):
    if len(field) != len(pattern):
        raise ValueError("field and pattern dimensions must match")
    return sum(p.conjugate() * f for p, f in zip(pattern, field))


def noisy(field, sigma, rng):
    if sigma < 0:
        raise ValueError("sigma must be non-negative")
    return normalize([
        value + complex(rng.gauss(0.0, sigma), rng.gauss(0.0, sigma))
        for value in field
    ])


def random_field(size, rng):
    if size <= 0:
        raise ValueError("size must be positive")
    return normalize([
        complex(rng.gauss(0.0, 1.0), rng.gauss(0.0, 1.0))
        for _ in range(size)
    ])


def median(values):
    values = sorted(values)
    if not values:
        return math.inf
    middle = len(values) // 2
    if len(values) % 2:
        return values[middle]
    return (values[middle - 1] + values[middle]) / 2.0


class Node:
    __slots__ = ("id", "x", "y", "stage", "modality")

    def __init__(self, node_id, x, y, stage, modality=None):
        self.id = node_id
        self.x = float(x)
        self.y = float(y)
        self.stage = stage
        self.modality = modality


class DirectedGeometry:
    """Seeded spatial graph with bidirectional local and forward stage edges."""

    def __init__(self, seed=42, k=4, links_per_target=2):
        if k <= 0 or links_per_target <= 0:
            raise ValueError("k and links_per_target must be positive")
        self.seed = seed
        self.k = k
        rng = random.Random(seed)
        self.nodes = []
        for stage, count, cx, cy, rx, ry, labels in STAGE_SPECS:
            made = 0
            attempts = 0
            while made < count and attempts < 20000:
                attempts += 1
                x = rng.uniform(cx - rx, cx + rx)
                y = rng.uniform(cy - ry, cy + ry)
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                    self.nodes.append(Node(len(self.nodes), x, y, stage,
                                           labels[made]))
                    made += 1
            while made < count:
                self.nodes.append(Node(len(self.nodes), cx, cy, stage,
                                       labels[made]))
                made += 1
        self.n = len(self.nodes)
        self._ids_by_stage = {
            stage: [node.id for node in self.nodes if node.stage == stage]
            for stage in STAGE_ORDER
        }
        self.edges = set()
        # Local links are restricted to a stage and explicitly bidirectional.
        for stage in STAGE_ORDER:
            ids = self._ids_by_stage[stage]
            for node_id in ids:
                node = self.nodes[node_id]
                near = sorted(
                    (self._distance2(node, self.nodes[other]), other)
                    for other in ids if other != node_id
                )[:k]
                for _, other in near:
                    self.edges.add((node_id, other))
                    self.edges.add((other, node_id))
        # Only these forward cross-stage transitions exist.
        self._add_links("sensory", "spinal", links_per_target)
        self.reflex_edges = self._add_links("spinal", "motor",
                                            links_per_target)
        self._add_links("spinal", "central", links_per_target)
        self._add_links("central", "motor", links_per_target)
        self.adjacency = [[] for _ in self.nodes]
        for source, target in sorted(self.edges):
            self.adjacency[source].append(target)
        self.stage_transition_counts = defaultdict(int)
        for source, target in self.edges:
            a = self.nodes[source].stage
            b = self.nodes[target].stage
            if a != b:
                self.stage_transition_counts[(a, b)] += 1

    @staticmethod
    def _distance2(a, b):
        return (a.x - b.x) ** 2 + (a.y - b.y) ** 2

    def _add_links(self, source_stage, target_stage, per):
        selected = set()
        targets = self._ids_by_stage[target_stage]
        for source in self._ids_by_stage[source_stage]:
            node = self.nodes[source]
            near = sorted(
                (self._distance2(node, self.nodes[target]), target)
                for target in targets
            )[:per]
            for _, target in near:
                self.edges.add((source, target))
                selected.add((source, target))
        return selected

    def ids(self, stage):
        return list(self._ids_by_stage[stage])

    def sensory_by_modality(self):
        result = {modality: [] for modality in MODALITIES}
        for node in self.nodes:
            if node.stage == "sensory":
                result[node.modality].append(node.id)
        return result

    def distances_from(self, source, removed_edges=()):
        removed = set(removed_edges)
        distances = [math.inf] * self.n
        distances[source] = 0.0
        heap = [(0.0, source)]
        while heap:
            distance, node_id = heapq.heappop(heap)
            if distance > distances[node_id]:
                continue
            node = self.nodes[node_id]
            for target in self.adjacency[node_id]:
                if (node_id, target) in removed:
                    continue
                other = self.nodes[target]
                candidate = distance + math.hypot(node.x - other.x,
                                                  node.y - other.y)
                if candidate < distances[target]:
                    distances[target] = candidate
                    heapq.heappush(heap, (candidate, target))
        return distances

    def ordered_route_distances(self, source, route, removed_edges=()):
        """Distances to final-stage nodes, constrained to route stage order."""
        if not route or len(set(route)) != len(route):
            raise ValueError("route must contain unique ordered stages")
        if any(stage not in STAGE_ORDER for stage in route):
            raise ValueError("unknown route stage")
        if self.nodes[source].stage != route[0]:
            raise ValueError("source must be in the route's first stage")
        removed = set(removed_edges)
        start = (source, 0)
        distances = {start: 0.0}
        heap = [(0.0, source, 0)]
        while heap:
            distance, node_id, stage_index = heapq.heappop(heap)
            state = (node_id, stage_index)
            if distance > distances[state]:
                continue
            node = self.nodes[node_id]
            for target in self.adjacency[node_id]:
                if (node_id, target) in removed:
                    continue
                next_stage = self.nodes[target].stage
                next_index = stage_index
                if next_stage != route[stage_index]:
                    if (stage_index + 1 >= len(route)
                            or next_stage != route[stage_index + 1]):
                        continue
                    next_index += 1
                edge_length = math.hypot(
                    node.x - self.nodes[target].x,
                    node.y - self.nodes[target].y,
                )
                candidate = distance + edge_length
                next_state = (target, next_index)
                if candidate < distances.get(next_state, math.inf):
                    distances[next_state] = candidate
                    heapq.heappush(heap, (candidate, target, next_index))
        final_index = len(route) - 1
        return {
            target: distances.get((target, final_index), math.inf)
            for target in self._ids_by_stage[route[-1]]
        }


class SyntheticMembrane:
    """Directed graph waves and normalized template scoring; synthetic only."""

    def __init__(self, seed=42, width=12.0, period=40.0):
        if width <= 0 or period <= 0:
            raise ValueError("width and period must be positive")
        self.geometry = DirectedGeometry(seed=seed)
        self.width = width
        self.period = period
        self._wave_cache = {}

    def wave(self, source):
        if source in self._wave_cache:
            return list(self._wave_cache[source])
        distances = self.geometry.distances_from(source)
        values = []
        for distance in distances:
            if math.isinf(distance):
                values.append(0j)
            else:
                amplitude = math.exp(-(distance * distance)
                                     / (2.0 * self.width * self.width))
                phase = 2.0 * math.pi * distance / self.period
                values.append(amplitude * complex(math.cos(phase),
                                                   math.sin(phase)))
        field = normalize(values)
        self._wave_cache[source] = field
        return list(field)

    def route_median(self, source, route, removed_edges=()):
        distances = self.geometry.ordered_route_distances(
            source, route, removed_edges=removed_edges)
        finite = [value for value in distances.values()
                  if math.isfinite(value)]
        return median(finite)


def class_scores(field, templates):
    return {
        label: abs(overlap(field, template))
        for label, template in templates.items()
    }


def predict(field, templates):
    scores = class_scores(field, templates)
    winner = max(scores, key=scores.get)
    return winner, scores[winner], scores


def calibrate_threshold(in_fields, ood_fields, templates, grid_step=0.005):
    if not in_fields or not ood_fields:
        raise ValueError("calibration requires both in-domain and OOD fields")
    if grid_step <= 0 or grid_step > 1:
        raise ValueError("grid_step must be in (0, 1]")
    in_scores = [predict(field, templates)[1] for field in in_fields]
    ood_scores = [predict(field, templates)[1] for field in ood_fields]
    steps = round(1.0 / grid_step)
    grid = [i / steps for i in range(steps + 1)]
    best_j = -math.inf
    best_thresholds = []
    for threshold in grid:
        sensitivity = sum(score >= threshold for score in in_scores) / len(in_scores)
        false_positive = sum(score >= threshold for score in ood_scores) / len(ood_scores)
        j = sensitivity - false_positive
        if j > best_j + 1e-12:
            best_j, best_thresholds = j, [threshold]
        elif abs(j - best_j) <= 1e-12:
            best_thresholds.append(threshold)
    return (best_thresholds[0] + best_thresholds[-1]) / 2.0, best_j


def decide(field, templates, threshold):
    label, score, scores = predict(field, templates)
    return ("accept" if score >= threshold else "reject"), label, score, scores

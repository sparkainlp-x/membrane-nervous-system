# Protocol amendment 1 — route reachability and conditional distances

**Date:** 2026-10-27

This is an additive amendment to the first local v0.2.0 record. It does not edit or replace `PROTOCOL.md`, `PROTOCOL_FREEZE.txt`, the original v0.2.0 results, or the original v0.2.0 ZIP. The amendment corrects interpretation and reporting of the route outcomes only.

## Immutable references

- Original frozen protocol SHA-256: `83f50f7744fd5f980cfc66b41d3d2c0bd41c7af8a7245dd1a855b30e3636037c`
- First-record `results/results.json` SHA-256: `e030007712cadd9c9ff6903d075f1930872b1d11022c8df8aea32794124114b2`
- First-record `results/per_seed.csv` SHA-256: `3fc0eb817fa89fda5f90ed510d82912315f9f43c1f28d3a8f8b42cffb2e1b1cb`
- First-record local ZIP SHA-256: `0527b90943b10a082682620df3bb1d69d696e86dfede0e0def49a610ea6892bb`

## Reason for the amendment

`ordered_route_distances()` returns a distance for every motor target and uses infinity for unreachable targets. The first v0.2 route summaries filtered out infinite distances before calculating medians. Those reported distances were therefore conditional medians among reachable targets, while the results omitted how many targets were unreachable. That made the reflex-versus-central distance comparison incomplete and not interpretable as a comparison of route coverage.

## Corrected route-only calculation

Recalculate route outcomes over exactly the original 100 deterministic geometry seeds (0–99), with the original source code, geometry, and stage-ordered routes. Do not regenerate classifier probes, noise, calibration samples, or OOD samples; do not change any random seed or classifier result. The deterministic route calculation uses no random draws.

For every geometry seed and every sensory source, report each route with all 32 motor targets in its coverage denominator:

- `reachable_targets`: count of finite distances;
- `unreachable_targets`: count of infinite distances;
- `total_motor_targets`: 32;
- `target_coverage`: reachable divided by 32;
- `median_distance_among_reachable_targets`: the conventional median of finite distances, or `null` when none are reachable.

Do not remove unreachable targets from the reachability denominator. Do not encode unreachable targets as zero distance. No single all-target distance median is introduced: when only some targets are reachable, distance summaries are explicitly conditional on reachability and must be read alongside coverage.

For each layout, also report total reachable/possible source-target pairs and layout coverage over 40 sensory sources × 32 motor targets (1,280 target opportunities per route). Report the 40 source-level coverage values, their minimum, and their mean. Across layouts, report mean source-layout coverage and the minimum source-layout coverage. Distance summaries retain the first protocol's hierarchy—median distance among reachable targets per source, then median across sensory sources within a layout—but label the result as conditional and report it only together with coverage.

Use only the already specified seeds and layouts. Any bootstrap interval for route-level layout summaries uses the original 2,000-replicate, seed-999 geometry-cluster procedure; it resamples the 100 existing layout summaries and does not generate new model data.

## Interpretation correction

The original v0.2.0 distance values must be described as **medians among reachable motor targets**. The original statement that the reflex route was shorter in 100/100 layouts is not interpretable as an overall route-order comparison without coverage. In particular, an apparently shorter distance can coexist with many unreachable targets. This amendment reports coverage explicitly and makes no biological or conduction-time claim.

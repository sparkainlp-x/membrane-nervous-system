# Corrigendum — seeded reconstruction wording

**Date:** 2026-10-27

This clarification preserves, and does not replace or modify, the frozen original v0.2 protocol or `PROTOCOL_AMENDMENT_2026-10-27.md` (SHA-256 `a1248cf3680dedf806c11610ab587211060e52f77a500eb12f83b7d607156270`).

The amendment's sentence that “the deterministic route calculation uses no random draws” was imprecise. To reconstruct the same geometries, `SyntheticMembrane(seed=0…99)` replays each original fixed-seed geometry generator. This is deterministic reconstruction of the same 100 layouts, not new seed selection or new stochastic probe generation. The route-distance calculations themselves are deterministic. The geometry-cluster bootstrap intervals use the already specified bootstrap RNG seed 999. No classifier benchmark, noisy probes, calibration probes, or OOD probes were regenerated. The route-only script verifies that the reconstructed per-layout conditional distance summaries exactly match the preserved first-record results.

No numeric result, analysis rule, or reported conclusion changes under this clarification.

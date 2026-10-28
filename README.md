# Membrane Nervous System

A reproducible **synthetic toy model** shaped like a simple sensory–spinal–central–motor network. It is not a biological nervous system, a medical device, or evidence about human physiology.

## Game video

Watch the [Nervous System Game video](https://muse.ai/s/nervous-system-game-bxd6gxnxdkpxq8t/3VawMNhoeXlu7gKsNULpeuroNqoHMWG0SIvXwcbq_Jc). The game is related to this synthetic toy model; it is not a biological nervous system or neuroscience evidence.

## What the results show

The latest v0.2.0 source package adds an imposed frequency-response layer and **synthetic parameter injection** to the earlier toy. It uses generated toy vectors and constructed parameter variants only: **no human data were used, and no human experiments were conducted**. In its fixed-seed demo, noisy-pattern acceptance rises modestly from **19/40 to 21/40**; random fields remain **0/40** accepted. The reported mean net score is **−0.276**, so the sampling did not pay for itself under the package’s stated cost. These are seeded software results, not human measurements or generalization evidence.

A separate v0.2 amendment corrected route-coverage reporting. Across 100 deterministic layouts, all 128,000 reflex source–target opportunities were reachable; central-route coverage was **92.125%** (117,920/128,000). Previously reported distance medians were conditional on reachable targets and excluded unreachable ones. The distances are arbitrary graph units—not conduction times—and the routes are synthetic graph properties, not neural pathways.

The separate frozen classifier benchmark reported **24.4%** macro accuracy for the centroid model and **25.3%** for the single-exemplar model, near the 25% balanced random-choice reference. It also rejected **0%** of equal-weight class-mixture probes in the tested out-of-distribution family. The review documents these limits alongside the v0.1 graph and test limitations.

The frequency layer is an imposed Gaussian centered at 7 Hz, using illustrative frequencies from another toy model. The source retains the historical module filename `human.py`, but contains no human inputs, dataset, participants, or experiments; no frequency response was measured in a person, and no therapeutic or medical claim is made.

## Contents

- `source/v0.1.0/` — clean source extracted from the preserved original v0.1.0 archive.
- `source/v0.2.0-synthetic-parameter-injection/` — source from the latest uploaded v0.2.0 ZIP, including its preregistration, design notes, demo, and tests.
- `source/v0.2-amendment/` — amended v0.2 source, frozen protocols, original and amended results, route-coverage code, tests, and the first-record archive.
- `archives/` — exact original v0.1.0, initial v0.2.0, latest synthetic parameter-injection v0.2.0, and amended v0.2.0 ZIPs. See `archives/SHA256SUMS.txt` for verified checksums.
- `docs/reviews/` — the scientific review and amended route-coverage review.
- `docs/provenance/` — the original amended-package checksum note.
- `LICENSE` — GNU Affero General Public License v3.0; the same license is retained in the source packages.

The archived latest v0.2.0 source ZIP is preserved byte-for-byte; its SHA-256 is recorded in the checksum file. The preserved original v0.1.0 archive is also unchanged.

## Reproduce the checks

Python 3 with the standard library is sufficient. Run each command from the indicated directory:

```bash
cd source/v0.1.0
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests -v
```

```bash
cd source/v0.2.0-synthetic-parameter-injection
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests test_human_injection -v
PYTHONDONTWRITEBYTECODE=1 python3 -B demo_v02.py
```

```bash
cd source/v0.2-amendment
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests test_route_coverage_amendment -v
```

## License

This repository is distributed under AGPL-3.0. See [`LICENSE`](LICENSE).

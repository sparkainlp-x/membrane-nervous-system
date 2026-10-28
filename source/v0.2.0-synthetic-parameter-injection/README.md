# membrane-nervous-system v0.2.0

**A sparkainlp-x membrane in a nervous-system-shaped toy — not a
nervous system.**

Stdlib-only Python, seeded, reproducible, AGPL-3.0-only.

**This is synthetic parameter injection only. It uses generated toy vectors and constructed parameter variants; no human data were used, and no human experiments were conducted.** The source module `human.py` retains its historical filename; it contains only an imposed frequency-sensitivity function, not human measurements or an experiment on people.

## Latest lineage reused

- **membrane-capacity**: complex oscillators, outer-product
  holographic memory, one-shot projection.
- **refusing-membrane / membrane-vs-hopfield**: REJECT iff max
  |overlap| < tau, tau calibrated once via Youden's J and frozen,
  midpoint-of-max-J improvement.
- **membrane-heart / membrane-brain**: waves stored as ENVELOPED
  phasor fields (pure phase was falsified in membrane-heart).
- **holo-heart-neurons / membrane-brain**: seeded neurons,
  k-nearest-neighbour edges, Dijkstra propagation delays.

## Run

```bash
python demo.py    # v0.1.0 numbers + gate + recognition + lesion toy
python demo_v02.py  # v0.2.0: synthetic frequency gate + parameter injection
python3 -m unittest tests test_human_injection -v  # 18 tests
```

## v0.2.0 — what was added

- **Synthetic frequency-sensitivity layer (`human.py`; historical filename)**: bands reused exactly from bentov-kuramoto (breath 0.25, heart 1.2, aorta 7.0, brain 10.0 Hz, illustrative only). Sensitivity is an IMPOSED Gaussian centred on the chosen sensitive frequency, 7.0 Hz (Bentov's alignment frequency), width 1.5 Hz: s(7.0) = 1.000, s(0.25) = 0.0000, s(1.2) = 0.0006, s(10.0) = 0.1353. A generated probe is scaled by s(f) without renormalising, so frequency moves the gate decision, not the winner. This curve is not fitted from people or human data.
- **Synthetic parameter injection (`injection.py`)**: on a rejection,
  commit p0 = 0.75, sample 20 constructed parameter variants (width
  [8, 20], period [30, 50]), revise by the fixed logistic rule
  from microtubule-crystallize, decide on the best variant vs
  the FROZEN tau, score Brier / points / net. Tau never moves,
  patterns are never added, rescued probes are never stored.

## Synthetic demo results (demo_v02, seed 42; PREREG.md bars all passed)

- Clean generated pain pattern: 7.0 Hz accept/withdraw; 0.25 Hz refuse; 10.0 Hz refuse
- Sigma 0.30, f 7.0 Hz: stock **19/40** accepted, injected
  **21/40** accepted — a modest rescue, not a cure
- Random generated fields, injected: **0/40** accepted
- Injected net score (mean over injected runs): **-0.276** —
  sampling improves acceptance slightly but does NOT pay for
  itself at c = 0.01 per sample, reported, not tuned away
- Tau after injection: 0.243 (unchanged), patterns still 4
- A first injection draft (re-noising the probe) FAILED the
  rescue bar (19/40 = 19/40) and was abandoned; see PREREG.md
  correction. Variants are parameter sets, as in the arena.

## The toy, in one paragraph

128 neurons in four stages: sensory 40 (touch 12, temperature 8,
pain 8, proprioception 12), spinal 32, central 24, motor 32
(flexor 16, extensor 16). Edges are 4-NN plus explicit cross-stage
edges, including a spinal->motor reflex arc. Four stored
"responses" are enveloped waves seeded at one sensory modality
each: pain -> withdraw, touch -> grasp, proprioception ->
balance, temperature -> cool-alert. A probe is projected onto
them: the membrane names one, or the frozen gate refuses it.

## Synthetic demo output (demo, seed 42)

- 128 neurons, 578 edges, 256 cross-stage, 64 reflex
- Pain seed: reflex median **53.52** distance units, central
  median **90.65** distance units
- Lesion toy (reflex edges cut, central excluded): reflex route
  **inf** — motor unreachable on the reflex route, while the
  central route remains finite
- Gate calibrated: tau = **0.243**, Youden J = **0.990** (frozen)
- Fresh noisy recognition (sigma = 0.15): **40/40**
- Fresh random fields refused: **50/50**
- Clean generated pain pattern: accept, withdraw

## Honest limits — read before any use

- **No human data or human experiments are included or reported.** This package only runs a synthetic simulation on generated vectors and parameter sets.
- **Not a human nervous system.** No receptors, ion channels,
  synapses with plasticity, spinal tracts, or cortex. The
  "stages" are four position zones; the "responses" are four
  wave snapshots; the "reflex" is a shorter graph path.
- **Not neuroscience, not a medical device, not a diagnosis,
  not a measurement of any real person.** The lesion toy says
  nothing about real lesions, reflexes, or patients.
- "Holographic" here = outer-product associative memory, the
  membrane meaning — not a laser hologram and not a display.
- Delays are in distance units, not milliseconds. Nothing here
  transfers to a real nervous system without a real neural model
  and real data, neither of which this package has or claims.

## Files

- `nervous.py` — geometry, waves, membrane, gate, routes (v0.1.0, unchanged)
- `human.py` — illustrative bands and an imposed synthetic frequency-sensitivity function (historical filename)
- `injection.py` — synthetic parameter-set sampling after rejection
- `demo.py` — v0.1.0 synthetic demo
- `demo_v02.py` — v0.2.0 synthetic demo
- `tests.py` — 8 v0.1.0 tests
- `test_human_injection.py` — 10 v0.2.0 synthetic logic tests (historical filename)
- `PREREG.md` — pre-registered computational bars + the sampling correction
- `DESIGN.md` — decisions, falsified designs, limits
- `LICENSE` — AGPL-3.0-only

## What else this would need to be more than a toy

- A real input: a sensor, a recording, a person — none of
  these exist in this package. Input here is a vector, not a
  measurement.
- Real human data with ground truth, to fit or test a
  sensitivity curve instead of imposing one.
- Any human or medical claim would need real data, a real
  neural model, and review outside this toy. None is claimed.
- This extracted source snapshot is now public at https://github.com/sparkainlp-x/membrane-nervous-system; the original upload ZIP remains byte-for-byte preserved in the repository's `archives/` directory. No DOI is claimed.

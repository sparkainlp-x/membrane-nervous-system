# membrane-nervous-system v0.1.0

**A sparkainlp-x membrane in a nervous-system-shaped toy — not a
nervous system.**

Stdlib-only Python, seeded, reproducible, AGPL-3.0-only.

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
python demo.py    # numbers + gate + recognition + lesion toy
python tests.py   # 8 tests
```

## The toy, in one paragraph

128 neurons in four stages: sensory 40 (touch 12, temperature 8,
pain 8, proprioception 12), spinal 32, central 24, motor 32
(flexor 16, extensor 16). Edges are 4-NN plus explicit cross-stage
edges, including a spinal->motor reflex arc. Four stored
"responses" are enveloped waves seeded at one sensory modality
each: pain -> withdraw, touch -> grasp, proprioception ->
balance, temperature -> cool-alert. A probe is projected onto
them: the membrane names one, or the frozen gate refuses it.

## Measured (demo, seed 42)

- 128 neurons, 578 edges, 256 cross-stage, 64 reflex
- Pain seed: reflex median **53.52** distance units, central
  median **90.65** distance units
- Lesion toy (reflex edges cut, central excluded): reflex route
  **inf** — motor unreachable on the reflex route, while the
  central route remains finite
- Gate calibrated: tau = **0.243**, Youden J = **0.990** (frozen)
- Fresh noisy recognition (sigma = 0.15): **40/40**
- Fresh random fields refused: **50/50**
- Clean pain probe: accept, withdraw

## Honest limits — read before any use

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

- `nervous.py` — geometry, waves, membrane, gate, routes
- `demo.py` — measured demo
- `tests.py` — 8 tests
- `DESIGN.md` — decisions, falsified designs, limits
- `LICENSE` — AGPL-3.0-only

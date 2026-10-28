# membrane-nervous-system v0.2.0

**Synthetic toy, not physiology.** This is a local software experiment using generated graph layouts and generated complex vectors. It does not model real receptors, neurons, synapses, reflexes, motor actions, patients, or clinical outcomes.

## What changed from v0.1.0

The v0.2 copy is separate; the supplied v0.1.0 archive is not edited. Within-stage nearest-neighbour links are bidirectional. Cross-stage links are directed only along the declared synthetic transitions. Reflex and central distances are calculated only on paths that follow their stated stage order. The lesion check removes every spinal-to-motor edge. The median now averages the middle pair for even-sized samples, and vector dimensions and calibration inputs are validated.

These are definitions of this toy graph. Distances are Euclidean path lengths in arbitrary geometry units, not conduction times. The layout was deliberately arranged and is not evidence that a reflex route is shorter in biology.

## Classification and its limits

The code stores generated, normalized phasor templates and scores probes by absolute complex overlap. It does **not** construct an outer-product weight matrix or simulate signals propagating into motor action. Normalized squared overlaps are relative scores, not calibrated probabilities. A rejection threshold is calibrated only on the synthetic training and OOD families specified in `PROTOCOL.md`; it is not general OOD-rejection evidence.

The benchmark freezes the source split and analysis plan before results are generated. It compares class-centroid and single-exemplar template classifiers on held-out synthetic sensory-node sources, with per-geometry cluster-bootstrap intervals. It has no real-world data and no biological interpretation.

## Run locally

```bash
python3 tests.py
python3 demo.py
python3 benchmark.py
```

`demo.py` is a fixed-seed illustration, not the benchmark. It prints calibration counts separately from fresh checks and reports both acceptance and expected-label correctness. `benchmark.py` writes `results.json` and `per_seed.csv` in a local `results/` folder. No package was published or uploaded.

The exact frozen analysis plan and its recorded SHA-256 are in `PROTOCOL.md` and `PROTOCOL_FREEZE.txt`.

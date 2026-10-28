# v0.2 local benchmark protocol (frozen before results)

**Purpose.** This is a local, synthetic software benchmark for a toy graph-and-template classifier. It does not test human neurobiology, clinical outcomes, or real nervous-system mechanisms. The original v0.1.0 archive, documentation, and demo results remain unchanged.

## Questions

1. Under an explicitly directed, stage-ordered graph, are the reflex and central route measurements well-defined, and does deleting every spinal-to-motor edge make only the constrained reflex route unreachable?
2. Does a four-class normalized-prototype classifier generalize from training sensory-node sources to held-out sensory-node sources better than a single-exemplar template and a 25% random-choice baseline?
3. How often does a max-overlap rejection gate accept held-out in-domain synthetic probes and reject out-of-domain (OOD) probes from prespecified synthetic families?

These are properties of this simulator and its generated distributions only.

## Frozen simulator and split

Use 100 geometry seeds, integers 0 through 99 inclusive. For each modality, sort sensory node IDs ascending; the first floor(n/2) IDs are training sources and all remaining IDs are held-out test sources. Do not move sources between sets or exclude seeds after seeing results. Keep the v0.1 stage sizes and position-zone layout, with k=4 nearest neighbors computed **within each stage only**. Make within-stage edges bidirectional. Add directed edges from each sensory node to its two nearest spinal nodes; from each spinal node to its two nearest motor nodes and two nearest central nodes; and from each central node to its two nearest motor nodes. No other cross-stage edges are allowed.

A wave is the v0.1 enveloped phasor formula (Gaussian amplitude, phase from graph distance, width=12, period=40), computed from shortest directed path distances. Every vector is L2-normalized. A route must follow exactly its declared ordered stages: reflex = sensory → spinal → motor; central = sensory → spinal → central → motor. Within-stage edges may be traversed in either direction; stage transitions may only move to the next stage in that route. Route summaries are medians over motor targets, then over sensory sources within a geometry. Distances are arbitrary simulator units, not time.

## Classifiers and probes

The four synthetic labels remain pain→withdraw, touch→grasp, proprioception→balance, and temperature→cool-alert. The **centroid model** stores the normalized mean of all training-source wave vectors for each modality. The **single-exemplar baseline** stores only the lowest-ID training-source wave for each modality and scores by absolute complex overlap. Both choose the class with the largest absolute overlap. Also report the 25% balanced random-choice reference; do not treat it as a trained model.

For every held-out sensory source, generate five independent complex-Gaussian perturbations at each sigma in {0.05, 0.15, 0.30}; normalize each perturbed vector. The source modality supplies the synthetic target label. Use deterministic per-geometry random streams derived from the geometry seed and separate calibration/test stream offsets.

## Rejection calibration and OOD families

Calibrate a separate threshold for each classifier using training sources only: five sigma=0.15 perturbations per training source are in-domain calibration probes. OOD calibration probes are 20 normalized complex-Gaussian random fields and 20 normalized equal-weight sums of two distinct class centroids. Select tau on the fixed grid {0, 0.005, …, 1}; maximize Youden J = sensitivity − false-positive rate and use the midpoint of all maximizing grid values. Freeze tau before evaluating held-out probes.

Test OOD rejection on fresh independent draws from both calibration families and on wave fields seeded at every spinal, central, and motor node. No OOD test field is used to fit tau. Report results separately by OOD family and pooled.

## Outcomes and uncertainty

For each classifier report, by sigma and pooled across sigma: macro-averaged four-class accuracy before rejection, acceptance/coverage on held-out in-domain probes, accuracy among accepted in-domain probes, and the per-seed centroid-minus-single-exemplar macro-accuracy difference. For OOD data report rejection rate separately by family and pooled. Summarize each outcome as the mean of per-geometry values with a 95% percentile cluster-bootstrap interval, resampling the 100 geometry seeds (2,000 resamples; bootstrap RNG seed 999). Do not calculate sample-level binomial intervals as though repeated probes from a geometry/source were independent.

For routes report the per-seed median reflex and central distances, the paired reflex-minus-central difference, and the fraction of seeds with a shorter reflex distance. For the lesion control, remove all spinal→motor edges and verify the constrained reflex route is unreachable for all sensory sources while the central route remains reachable.

## Integrity and reporting rules

Write all generated data and metrics to new v0.2 result files. Preserve the original v0.1.0 ZIP and its preregistration/results if present. No preregistration or separate results file was present in the supplied archive. Report all benchmark data as generated synthetic data. Do not claim biological validity, real-world accuracy, statistical evidence about humans, or a measured reflex. Do not publish or upload the package. If implementation defects force a protocol change, stop, document an amended protocol with a new version and hash before regenerating any results; never silently revise this frozen protocol.

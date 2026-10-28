# Scientific review: membrane-nervous-system v0.1.0 and local v0.2 pass

## Bottom line

The supplied ZIP is an honestly labeled, reproducible **synthetic toy**, not evidence about human physiology. Its own documentation says it has no receptors, ion channels, synaptic plasticity, spinal tracts, or cortex. The main scientific issue is that v0.1 describes graph distances as directional routes even though its graph is undirected and its path calculations do not enforce the stated stage order. The 40/40 demo figure is an acceptance count, not a correctness count.

A separate local v0.2 copy fixes the route definitions and input/statistic defects without changing the original ZIP. Its frozen 100-layout benchmark finds that the template classifier does not generalize to held-out synthetic sensory sources: balanced label accuracy is about the 25% random-choice reference. Its gate also accepts every test mixture of two class templates, so it does not support a broad out-of-distribution rejection claim.

## What is in the supplied ZIP

The archive contains `nervous.py`, `demo.py`, `tests.py`, `README.md`, `DESIGN.md`, `CITATION.cff`, and the license. It does not contain a separate preregistration, dataset, or results file. The original eight tests pass, and the seed-42 demo reproduces its printed counts. The archive was left unchanged; its SHA-256 is `c6d5498e4bbc2eaa3e494fecde3d913397b876c844bb88faea722367a866016a`.

## Important v0.1 limitations

**The routes are graph distances, not signal transmission.** In `nervous.py`, edges are stored as unordered node pairs and `neighbours()` traverses both directions. `reflex_time()` merely excludes central nodes; it does not require a sensory→spinal→motor path. `central_time()` adds unrestricted full-graph distances to and from a central node, so it does not enforce sensory→spinal→central→motor order. These values cannot be interpreted as neural pathways or conduction times.

The README’s seed-42 figures of 53.52 and 90.65 are arbitrary geometry units, and the layout was deliberately chosen to make the first value smaller. There is also a summary-statistic issue: for 32 motor targets, the original `median()` returns the upper middle value rather than averaging the two middle values. The conventional even-count medians for those same v0.1 calculations are approximately 53.46 and 90.24. The test suite checks only one seed’s route inequality and lesion reachability.

The README says there are 256 cross-stage edges, but that count is only the explicitly tagged links. At seed 42 the actual graph has 257 unique cross-stage pairs because global k-nearest-neighbour construction adds one untagged sensory-to-central edge. This is another reason the v0.1 graph does not encode the claimed stage hierarchy.

**The classifier is a template matcher.** It scores four stored complex-field templates by absolute overlap. The implementation does not build an outer-product weight matrix. Its normalized squared overlaps are relative scores, not calibrated probabilities. The rejection threshold is tuned on specific generated noisy templates and normalized random fields; its Youden J is a calibration-sample statistic, not general evidence about arbitrary unfamiliar inputs.

**The original demo’s “40/40 recognition” label is too strong.** `demo.py` increments the count whenever a probe is accepted, without checking whether the predicted response matches the expected label. Reproducing its seed-42 streams confirms 40/40 were accepted, and a separate explicit comparison also finds 40/40 expected labels correct in this one synthetic check. Those are distinct facts. For 40/40 successes, the Wilson 95% interval is about 91.2–100%. For 0 false accepts among 50 random-field probes, the Wilson 95% interval is about 0–7.1%. These intervals describe only this small fixed-seed synthetic check; they do not establish generalization.

The original code also silently truncates vectors of the wrong length through `zip()` in `overlap()` and does not validate empty calibration sets or invalid grids. The eight tests do not cover those cases or check all noisy expected labels.

## Separate v0.2 results

The original ZIP and extracted source were not edited. The local v0.2 copy uses directed cross-stage links, bidirectional within-stage links, and route algorithms constrained to the declared stage order. The lesion removes every spinal-to-motor link. It also uses the conventional even-sample median, validates vector dimensions and calibration inputs, and adds regression tests. All ten v0.2 tests pass.

The local analysis plan was frozen before benchmark generation and is checksum-recorded in `v0.2/PROTOCOL_FREEZE.txt`. This is a local frozen protocol, not a claim of external preregistration. It evaluated 100 generated geometries. The split held out sensory-node sources by modality. Calibration used 10,000 in-domain and 4,000 OOD probes; evaluation used 30,000 held-out in-domain and 12,800 OOD probes. Confidence intervals resample geometry seeds as clusters, rather than treating repeated probes from the same layout as independent.

The centroid classifier reached **24.4% macro label accuracy** (seed-clustered 95% interval 23.1–25.6%). The single-exemplar model reached **25.3%** (23.8–26.8%). Both intervals include the 25% balanced random-choice reference. Among accepted in-domain probes, macro accuracy was still only 24.5% for the centroid model and 25.2% for the single-exemplar model. Thus the upgrade does not show useful held-out label generalization under this synthetic design.

The gate’s performance depended strongly on the chosen OOD family. It rejected 89.4% of random fields and 95.5% of non-sensory-source waves for the centroid model, but rejected **0% of equal-weight class-mixture probes**. For the single-exemplar model the corresponding rates were 83.1%, 94.8%, and **0%**. The pooled rejection rates (79.6% and 78.2%) are weighted averages dominated by the larger non-sensory-source family; the per-family rates are more informative. Mean calibration Youden J was 0.411 for the centroid model and 0.255 for the single-exemplar model, again only for the specified generated calibration distributions.

Across the 100 geometries, the median reflex-route distance averaged 54.92 arbitrary units (95% interval 54.63–55.22) and the central-route distance averaged 91.74 (90.03–93.21). The reflex route was shorter in 100/100 layouts because of the prescribed geometry and edge rules. The lesion invariant passed for all sensory sources in all 100 layouts. These are software/topology checks only, not biological findings or timing measurements.

The v0.2 seed-42 demo prints “SYNTHETIC TOY, NOT PHYSIOLOGY” first, separates its 100+100 calibration probes from fresh 40+50 checks, and reports acceptance and expected-label correctness separately. It is an illustration, not the multi-seed benchmark.

## Files

The separate implementation and complete local results are in the v0.2 directory. The benchmark outputs retain per-seed metrics and generated-data counts so the reported summaries can be inspected. Nothing was published or uploaded.

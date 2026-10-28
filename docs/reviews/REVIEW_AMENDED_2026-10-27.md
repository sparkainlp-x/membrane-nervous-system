# Route-coverage amendment — membrane-nervous-system v0.2.0

This dated addendum corrects route reporting in the first v0.2.0 record. It does not replace or overwrite the original frozen protocol, results, ZIP, or earlier review. The additive amendment SHA-256 is `a1248cf3680dedf806c11610ab587211060e52f77a500eb12f83b7d607156270`; a wording corrigendum is separately hash-recorded as `10d1c14db8b3984cf462c368d8b8724a87173dface39e3fac911e9f9b870c48d`.

## What the added coverage shows

The route calculation returned distances for all 32 motor targets, including infinity for unreachable targets. The original summaries filtered out infinite distances before taking medians. Therefore, the old route distances were **medians among reachable motor targets**, not medians over all motor targets, and the first report omitted how often targets were unreachable.

On the same 100 deterministic layouts, reflex coverage was **100%**: all 128,000 sensory-source–motor-target opportunities were reachable. Central-route coverage was **92.125%** (117,920 of 128,000 reachable; 10,080 unreachable). Across the 4,000 source-layout pairs, the lowest central coverage was **15.625%**—5 of 32 targets, for seed 2, source 0—and the highest was 100%. The geometry-clustered 95% interval for mean central layout coverage is 87.75–95.97%. In 600 of 4,000 central source-layout pairs, at least one target was unreachable; none had zero reachable motor targets.

The route-distance figures remain **conditional medians among reachable targets**: the mean of layout-level medians was 54.920 arbitrary units for reflex routes (95% cluster-bootstrap interval 54.628–55.218) and 91.744 for central routes (90.150–93.294). The reflex conditional median was shorter in 100/100 layouts. However, the v0.2.0 route-order comparison is **not interpretable without coverage**: the central route’s target reachability varied substantially, and the distances exclude unreachable targets. No single all-target distance median has been added; coverage uses all targets while distance medians are explicitly conditional on reachable targets.

These are deterministic properties of the synthetic graph only. They are not neural pathways, measured reflexes, or conduction times.

## What changed—and what did not

The amended calculation deterministically reconstructs only the original geometry seeds 0–99 and verifies that its conditional medians match the first-record per-seed values. The fixed-seed geometry replay is not new randomized model data; the bootstrap uses the already specified seed 999. The classifier benchmark was not rerun, and no noisy probes, calibration samples, or OOD samples were regenerated. The original source, frozen protocol, benchmark results, first ZIP, and earlier review are unchanged. New per-source/layout and per-layout coverage files are in `v0.2-amendment/results/`.

The original uploaded v0.1.0 archive remains unchanged; its verified SHA-256 is `c6d5498e4bbc2eaa3e494fecde3d913397b876c844bb88faea722367a866016a`. Nothing was published.

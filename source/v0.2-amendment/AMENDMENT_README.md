# Route-coverage amendment package

This is an additive local package copy for the dated amendment. The first v0.2.0 ZIP remains separately preserved and unchanged at the workspace root; an identical copy is included under `first_record/`. The original protocol, source files, and benchmark results are also copied intact. The dated amendment and wording corrigendum have separate hash records.

The first v0.2 benchmark results remain `results/results.json` and `results/per_seed.csv`. The amended route-only calculation adds:

- `results/route_coverage_amendment_2026-10-27.json`
- `results/route_coverage_by_source_layout_2026-10-27.csv`
- `results/route_coverage_by_layout_2026-10-27.csv`

The additional script `recalculate_route_coverage.py` recalculates only route distances and reachability for deterministic geometry seeds 0–99. It checks the first-record hashes and verifies that the earlier conditional distance summaries are reproduced. When run from an extracted package, it checks the included first-record ZIP. It does not rerun the classifier benchmark or generate new classifier probes. The amendment regression suite is `test_route_coverage_amendment.py`.

For the corrected plain-language interpretation, see `REVIEW_AMENDED_2026-10-27.md`. All results are synthetic graph properties, not physiology.

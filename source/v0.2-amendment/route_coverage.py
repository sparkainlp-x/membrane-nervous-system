"""Coverage-preserving summaries for stage-ordered synthetic routes."""
import math

from nervous_v2 import median


def summarize_target_distances(target_distances):
    """Summarize distances without hiding unreachable targets.

    Distances are reported only among reachable targets. All targets remain in
    the coverage denominator, and the number of infinite distances is explicit.
    """
    if not target_distances:
        raise ValueError("at least one motor target is required")
    values = list(target_distances.values())
    if any(math.isnan(value) or value < 0 for value in values):
        raise ValueError("distances must be non-negative and not NaN")
    reachable = [value for value in values if math.isfinite(value)]
    total = len(values)
    count = len(reachable)
    return {
        "total_motor_targets": total,
        "reachable_targets": count,
        "unreachable_targets": total - count,
        "target_coverage": count / total,
        "median_distance_among_reachable_targets": (
            median(reachable) if reachable else None
        ),
    }


def summarize_layout(source_summaries):
    """Summarize all sensory-source × motor-target opportunities in a layout."""
    if not source_summaries:
        raise ValueError("at least one sensory source is required")
    total = sum(row["total_motor_targets"] for row in source_summaries)
    reachable = sum(row["reachable_targets"] for row in source_summaries)
    source_coverage = [row["target_coverage"] for row in source_summaries]
    conditional_source_medians = [
        row["median_distance_among_reachable_targets"]
        for row in source_summaries
        if row["median_distance_among_reachable_targets"] is not None
    ]
    return {
        "sensory_sources": len(source_summaries),
        "source_target_opportunities": total,
        "reachable_source_target_pairs": reachable,
        "unreachable_source_target_pairs": total - reachable,
        "target_coverage": reachable / total,
        "mean_source_target_coverage": sum(source_coverage) / len(source_coverage),
        "min_source_target_coverage": min(source_coverage),
        "max_source_target_coverage": max(source_coverage),
        "sources_with_no_reachable_motor_targets": sum(
            row["reachable_targets"] == 0 for row in source_summaries
        ),
        "source_rows_with_reachable_motor_targets": len(
            conditional_source_medians
        ),
        "median_of_source_medians_among_reachable_targets": (
            median(conditional_source_medians)
            if conditional_source_medians else None
        ),
    }

"""Compute descriptive summaries from the supplied synthetic cases; stdlib only."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path)
    args = parser.parse_args()
    fixture_bytes = args.fixture.read_bytes()
    fixture = json.loads(fixture_bytes.decode("utf-8-sig"))
    cases = {case["id"]: case["evidence"] for case in fixture["cases"]}
    method = cases["method"]
    baseline_accuracy = method["baseline_accuracy_percent"]
    cache_accuracy = method["cache_accuracy_percent"]
    baseline_latency = method["baseline_latency_ms"]
    cache_latency = method["cache_latency_ms"]
    if not all(len(values) == 3 for values in
               (baseline_accuracy, cache_accuracy, baseline_latency, cache_latency)):
        raise ValueError("Expected three paired training-seed summaries.")
    accuracy_deltas = [c - b for b, c in zip(baseline_accuracy, cache_accuracy)]
    latency_deltas = [c - b for b, c in zip(baseline_latency, cache_latency)]
    baseline_mean_latency = statistics.mean(baseline_latency)
    cache_mean_latency = statistics.mean(cache_latency)
    mixed = cases["mixed"]["paired_deltas"]
    if len(mixed) != 8:
        raise ValueError("Expected the eight prespecified task deltas.")
    result = {
        "data_kind": "synthetic acceptance fixtures, never research results",
        "source": {
            "file": args.fixture.name,
            "sha256": hashlib.sha256(fixture_bytes).hexdigest(),
            "fixture_version": fixture["version"],
            "inspected_cases": ["method", "theory", "mixed", "benchmark"],
        },
        "method": {
            "source_locator": "cases[id=method].evidence",
            "paired_accuracy_delta_pp": accuracy_deltas,
            "mean_baseline_accuracy_percent": statistics.mean(baseline_accuracy),
            "mean_cache_accuracy_percent": statistics.mean(cache_accuracy),
            "mean_accuracy_delta_pp": statistics.mean(accuracy_deltas),
            "sample_sd_of_accuracy_deltas_pp": statistics.stdev(accuracy_deltas),
            "paired_latency_delta_ms": latency_deltas,
            "mean_baseline_latency_ms": baseline_mean_latency,
            "mean_cache_latency_ms": cache_mean_latency,
            "mean_latency_delta_ms": statistics.mean(latency_deltas),
            "sample_sd_of_latency_deltas_ms": statistics.stdev(latency_deltas),
            "reduction_from_ratio_of_mean_latencies_percent":
                100 * (baseline_mean_latency - cache_mean_latency) / baseline_mean_latency,
            "ratio_of_mean_latencies": baseline_mean_latency / cache_mean_latency,
            "sampling_unit": "three paired training seeds on one fixed evaluation set",
            "examples_per_seed": method["n_examples_per_seed"],
            "intervals": None,
            "interval_reason": "Descriptive summaries only; no equivalence margin supplied.",
        },
        "mixed": {
            "source_locator": "cases[id=mixed].evidence.paired_deltas",
            "task_deltas_pp": mixed,
            "sum_delta_pp": sum(mixed),
            "mean_delta_pp": statistics.mean(mixed),
            "median_delta_pp": statistics.median(mixed),
            "sample_sd_across_task_deltas_pp": statistics.stdev(mixed),
            "minimum_delta_pp": min(mixed),
            "maximum_delta_pp": max(mixed),
            "positive_count": sum(delta > 0 for delta in mixed),
            "negative_count": sum(delta < 0 for delta in mixed),
            "zero_count": sum(delta == 0 for delta in mixed),
            "posthoc_positive_subset_mean_pp": statistics.mean(
                [delta for delta in mixed if delta > 0]),
            "sampling_unit": "eight prespecified tasks, each evaluated once",
            "intervals": None,
            "interval_reason": "No repeated-seed data or task-population sampling design supplied.",
        },
        "execution": {
            "dependencies": "Python standard library only",
            "new_experiments_run": 0,
            "external_model_calls": 0,
            "web_requests": 0,
            "interpretation": "Arithmetic on supplied synthetic summaries only",
        },
    }
    output = Path(__file__).resolve().parent / "case_calculations.json"
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
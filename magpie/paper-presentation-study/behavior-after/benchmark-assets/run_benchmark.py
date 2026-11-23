#!/usr/bin/env python3
"""Render the supplied synthetic aggregate fixture without generating observations."""
from __future__ import annotations
import argparse
import csv
import hashlib
import importlib.metadata as metadata
import json
import math
import os
from pathlib import Path
import platform


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_fixture(fixture: dict, record: dict) -> None:
    if fixture["data_kind"] != "synthetic fixture":
        raise ValueError("This example requires its labeled synthetic fixture")
    if record["status"] != "ready" or record["width_inches"] != fixture["paper_width_inches"]:
        raise ValueError("Missing data or changed display width")
    if record["data_kind"] != "illustrative":
        raise ValueError("Synthetic fixture must map to the renderer's illustrative data kind")
    if len(record["rows"]) != len(fixture["rows"]):
        raise ValueError("Aggregate row count changed")
    for original, rendered in zip(fixture["rows"], record["rows"], strict=True):
        for key in ("attempted", "successful", "failed"):
            value = original[key]
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError("Counts must be nonnegative integers")
        if original["attempted"] <= 0 or original["attempted"] != original["successful"] + original["failed"]:
            raise ValueError("Attempt accounting is inconsistent")
        for key in ("method", "attempted", "successful", "failed", "mean_success_latency_seconds"):
            if original[key] != rendered[key]:
                raise ValueError("The CSV and the original aggregate fixture disagree")
        expected = original["successful"] / original["attempted"]
        if not math.isclose(rendered["success_rate"], expected, rel_tol=0, abs_tol=1e-12):
            raise ValueError("Wrong success denominator")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "outputs")
    parser.add_argument("--reproduce-to", type=Path, help="Optional second render for a local reproducibility check")
    args = parser.parse_args()
    bundle = Path(__file__).resolve().parent
    output = args.output.resolve()
    os.environ.setdefault("MPLCONFIGDIR", str(output.parent / ".matplotlib-cache"))
    # Fixed export metadata and SVG IDs make local asset hashes comparable.
    os.environ["SOURCE_DATE_EPOCH"] = "0"
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams["svg.hashsalt"] = "synthetic-benchmark-v1"
    import render_evidence

    fixture = json.loads((bundle / "fixture.json").read_text(encoding="utf-8"))
    spec = bundle / "evidence-spec.json"
    evidence = render_evidence.load_evidence(spec)
    validate_fixture(fixture, evidence)
    result = render_evidence.render(spec, output)
    if result["status"] != "rendered":
        raise RuntimeError("Rendering did not complete")
    with (output / "table.csv").open(encoding="utf-8", newline="") as stream:
        table = list(csv.DictReader(stream))
    for row, original in zip(table, fixture["rows"], strict=True):
        for key in ("attempted", "successful", "failed"):
            if int(row[key]) != original[key]:
                raise AssertionError("A table count changed")
        if float(row["success_rate"]) != original["successful"] / original["attempted"]:
            raise AssertionError("A table success denominator changed")
        if float(row["mean_success_latency_seconds"]) != original["mean_success_latency_seconds"]:
            raise AssertionError("Conditional latency changed")

    checks = {"fixture_csv_agreement": True, "attempt_accounting": True, "table_known_answers": True}
    # These are parser/interface checks, not new agent runs or observations.
    checks["missing_zero_success_latency_stays_missing"] = render_evidence._latency({"mean_success_latency_seconds": ""}, 0, 2) is None
    try:
        render_evidence._latency({"mean_success_latency_seconds": "0"}, 0, 2)
    except ValueError:
        checks["latency_with_zero_successes_rejected"] = True
    else:
        checks["latency_with_zero_successes_rejected"] = False
    try:
        render_evidence._count({"attempted": "-1"}, "attempted", 2)
    except ValueError:
        checks["negative_attempt_count_rejected"] = True
    else:
        checks["negative_attempt_count_rejected"] = False
    if not all(checks.values()):
        raise AssertionError("An evidence-interface check failed")

    reproduction = {"performed": False, "kind": "rendering only; no research experiment"}
    if args.reproduce_to is not None:
        second = args.reproduce_to.resolve()
        if second == output:
            raise ValueError("The reproduction destination must be distinct")
        repeated = render_evidence.render(spec, second)
        matches = {name: digest(output / name) == digest(second / name) for name in render_evidence.OWNED_OUTPUTS}
        reproduction.update({"performed": True, "render_status": repeated["status"], "scientific_rows_identical": result["rows"] == repeated["rows"], "output_hash_matches": matches})
        if not reproduction["scientific_rows_identical"] or not all(matches.values()):
            raise AssertionError("The same-input render did not reproduce")

    inputs = ["fixture.json", "aggregate.csv", "evidence-spec.json", "render_evidence.py", "run_benchmark.py", "requirements.txt", "validation-requirements.txt", "README.md", "caption.md"]
    versions = {name: metadata.version(name) for name in ("matplotlib", "numpy", "pillow", "fonttools", "contourpy", "cycler", "kiwisolver", "packaging", "pyparsing", "python-dateutil", "six")}
    provenance = {
        "schema_version": 1, "analysis_revision": "benchmark-v1", "status": "executed",
        "data_kind": fixture["data_kind"], "renderer_data_kind": "illustrative",
        "data_kind_mapping": "Synthetic fixture uses the renderer's illustrative label; these are not measured research results.",
        "inputs_sha256": {name: digest(bundle / name) for name in inputs},
        "outputs_sha256": {name: digest(output / name) for name in render_evidence.OWNED_OUTPUTS},
        "dependency_record": {"python": platform.python_version(), "runtime": versions, "optional_pdf_validation": {"pypdf": metadata.version("pypdf")}},
        "portable_invocation": "python -X utf8 -B run_benchmark.py --output outputs",
        "export_metadata": {"SOURCE_DATE_EPOCH": "0", "meaning": "Fixed reproducibility metadata, not a research or execution date", "svg_hashsalt": "synthetic-benchmark-v1"},
        "checks": checks, "reproduction": reproduction,
        "scientific_content": {
            "question": fixture["question"], "rows": result["rows"],
            "success_denominator": "all 20 attempted tasks for each method",
            "latency_population": "successful attempts only; 16 for reference and 14 for candidate",
            "uncertainty": fixture["uncertainty"],
            "comparison_limits": "Success subsets may differ. Pairwise task outcomes, failure latency, repeated-run variability, and overall utility are unavailable.",
            "display_width_inches": fixture["paper_width_inches"]
        },
        "operations": {"primary_renders": 1, "reproduction_renders": int(args.reproduce_to is not None), "research_experiments": 0, "network_calls": 0, "package_installs": 0},
        "inspection_status": "This entry point executes generation and data checks; separate visual/PDF inspection must be recorded by its caller."
    }
    (output / "bundle-provenance.json").write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "executed", "checks": checks, "reproduction": reproduction, "rows": result["rows"], "outputs": list(render_evidence.OWNED_OUTPUTS) + ["bundle-provenance.json"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
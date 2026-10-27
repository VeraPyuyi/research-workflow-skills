"""Reproduce a synthetic aggregate table and SVG using Python's standard library."""
import csv
import hashlib
from html import escape
import json
import math
from pathlib import Path
import platform
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
INPUT_NAME = "benchmark_input.json"
CAPTION = (
    "Synthetic aggregate comparison of two agents under the same 20-task protocol. "
    "The reference succeeds on 16/20 tasks (80%); the candidate succeeds on 14/20 "
    "(70%). Mean latency among successful attempts is 15 s (n=16) and 10 s "
    "(n=14), respectively. These means condition on potentially different "
    "successful tasks. Failure latencies and task-level variability are "
    "unavailable; no uncertainty intervals or overall-latency estimate are shown."
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_rows(path):
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    expected = {"schema_version", "data_kind", "source", "question", "rows",
                "uncertainty", "paper_width_inches"}
    if set(data) != expected or data["schema_version"] != 1:
        raise ValueError("Use the sanitized version-1 aggregate input.")
    if data["data_kind"] != "synthetic fixture":
        raise ValueError("This example is restricted to its synthetic fixture.")
    if not isinstance(data["rows"], list) or len(data["rows"]) != 2:
        raise ValueError("Expected exactly two aggregate rows.")
    required = {"method", "attempted", "successful", "failed",
                "mean_success_latency_seconds"}
    rows = []
    for raw in data["rows"]:
        if set(raw) != required:
            raise ValueError("A row has missing or unexpected fields.")
        row = dict(raw)
        for key in ("attempted", "successful", "failed"):
            if type(row[key]) is not int or row[key] < 0:
                raise ValueError("Counts must be nonnegative integers.")
        if row["attempted"] == 0:
            raise ValueError("An empty denominator has no defined success rate.")
        if row["successful"] + row["failed"] != row["attempted"]:
            raise ValueError("Successful and failed counts must sum to attempted.")
        latency = row["mean_success_latency_seconds"]
        if row["successful"] == 0:
            if latency is not None:
                raise ValueError("No successes requires a null successful latency.")
        elif (type(latency) not in (int, float) or
              not math.isfinite(latency) or latency < 0):
            raise ValueError("Successful latency must be a finite nonnegative number.")
        row["success_percent"] = 100 * row["successful"] / row["attempted"]
        row["failure_percent"] = 100 * row["failed"] / row["attempted"]
        row["mean_success_latency_n"] = row["successful"]
        rows.append(row)
    # Fixed values also bind the caption and display limits to this exact fixture.
    signatures = [(r["method"], r["attempted"], r["successful"], r["failed"],
                   r["mean_success_latency_seconds"]) for r in rows]
    if signatures != [("reference", 20, 16, 4, 15.0),
                      ("candidate", 20, 14, 6, 10.0)]:
        raise ValueError("Changed evidence requires revising the example and caption.")
    if data["paper_width_inches"] != 3.25:
        raise ValueError("The supplied paper width must be 3.25 inches.")
    return data, rows


def write_table(rows):
    fields = ["method", "attempted", "successful", "failed", "success_percent",
              "failure_percent", "mean_success_latency_seconds",
              "mean_success_latency_n"]
    csv_path = ROOT / "benchmark_table.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({key: row[key] for key in fields} for row in rows)
    lines = [
        "# Synthetic aggregate comparison", "",
        "| Agent | Attempted | Successful | Failed | Success (%) | Failure (%) | Mean successful latency (s) | Latency n |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f'| {row["method"]} | {row["attempted"]} | {row["successful"]} | '
            f'{row["failed"]} | {row["success_percent"]:.1f} | '
            f'{row["failure_percent"]:.1f} | '
            f'{row["mean_success_latency_seconds"]:.1f} | '
            f'{row["mean_success_latency_n"]} |')
    lines.extend([
        "", "Each agent's success and failure rates use all 20 attempted tasks.",
        "Latency is the supplied mean over successes only, with n=16 or n=14.",
        "Different successful subsets prevent a matched-task speed comparison.",
        "No per-task values, failure latencies, or variability were supplied.",
        "Uncertainty intervals and all-attempt mean latencies are not estimated.",
        "These are synthetic acceptance data, not research measurements.", "",
    ])
    md_path = ROOT / "benchmark_table.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return [csv_path, md_path]


def write_figure(data, rows):
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" width="3.25in" height="3in" '
        'viewBox="0 0 234 216" role="img" aria-labelledby="title description">',
        '<title id="title">Synthetic agent reliability and successful latency</title>',
        '<desc id="description">Reference: 16 successes and 4 failures in 20 '
        'attempts, with mean successful latency 15 seconds. Candidate: 14 '
        'successes and 6 failures in 20 attempts, with mean successful latency '
        '10 seconds. Latency conditions on successes; no variability is supplied.</desc>',
        '<rect width="234" height="216" fill="white"/>',
        '<g font-family="DejaVu Sans, sans-serif" font-size="8" fill="#17212b">',
    ]

    def text(x, y, value, size=8, anchor="start", weight="normal", fill="#17212b"):
        parts.append(f'<text x="{x:g}" y="{y:g}" font-size="{size:g}" '
                     f'text-anchor="{anchor}" font-weight="{weight}" '
                     f'fill="{fill}">{escape(str(value))}</text>')

    def line(x1, y1, x2, y2, color="#66717c"):
        parts.append(f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" '
                     f'y2="{y2:g}" stroke="{color}" stroke-width="0.65"/>')

    def rect(x, y, width, height, fill):
        parts.append(f'<rect x="{x:g}" y="{y:g}" width="{width:g}" '
                     f'height="{height:g}" fill="{fill}"/>')

    text(10, 14, "Synthetic evaluation summary", 10, weight="bold")
    text(10, 27, "Same 20-task protocol", 8)
    text(10, 43, "A  Outcomes out of 20 attempts", 9, weight="bold")
    left, plot_width = 67, 144
    for row, top in zip(rows, (52, 75)):
        text(10, top + 10, row["method"])
        success_width = plot_width * row["successful"] / row["attempted"]
        rect(left, top, success_width, 14, "#176b5b")
        rect(left + success_width, top, plot_width - success_width, 14, "#c3c8ce")
        label = f'{row["successful"]}/20 ({row["success_percent"]:.0f}%)'
        text(left + success_width / 2, top + 10, label, anchor="middle", fill="white")
        text(left + success_width + (plot_width - success_width) / 2,
             top + 10, row["failed"], anchor="middle")
    line(left, 94, left + plot_width, 94)
    for value in (0, 5, 10, 15, 20):
        x = left + plot_width * value / 20
        line(x, 94, x, 97)
        text(x, 106, value, anchor="middle")
    rect(67, 113, 7, 7, "#176b5b")
    text(78, 120, "Successful")
    rect(153, 113, 7, 7, "#c3c8ce")
    text(164, 120, "Failed")
    text(10, 138, "B  Mean successful latency (s)", 9, weight="bold")
    for row, y in zip(rows, (159, 181)):
        text(10, y + 3, row["method"])
        x = left + plot_width * row["mean_success_latency_seconds"] / 20
        parts.append(f'<circle cx="{x:g}" cy="{y:g}" r="3.2" fill="#243a54"/>')
        label = (f'{row["mean_success_latency_seconds"]:g} s; '
                 f'n={row["mean_success_latency_n"]}')
        text(x, y - 7, label, anchor="middle")
    line(left, 189, left + plot_width, 189)
    for value in (0, 10, 20):
        x = left + plot_width * value / 20
        line(x, 189, x, 192)
        text(x, 201, value, anchor="middle")
    text(10, 213, "No variability supplied; intervals omitted.", 8)
    parts.extend(["</g>", "</svg>", ""])
    svg = "\n".join(parts)
    parsed = ET.fromstring(svg)
    if parsed.attrib["width"] != f'{data["paper_width_inches"]}in':
        raise ValueError("Figure width does not match the supplied paper width.")
    output = ROOT / "benchmark_figure.svg"
    output.write_text(svg, encoding="utf-8")
    return output


def main():
    input_path = ROOT / INPUT_NAME
    data, rows = load_rows(input_path)
    outputs = write_table(rows)
    outputs.append(write_figure(data, rows))
    caption_path = ROOT / "benchmark_caption.txt"
    caption_path.write_text(CAPTION + "\n", encoding="utf-8")
    outputs.append(caption_path)
    reference, candidate = rows
    provenance = {
        "schema_version": 1,
        "data_kind": data["data_kind"],
        "source": data["source"],
        "input": {"file": INPUT_NAME, "sha256": digest(input_path)},
        "implementation": {"file": "benchmark.py", "sha256": digest(Path(__file__))},
        "runtime": {"python_version": platform.python_version(),
                    "dependencies": "Python standard library only",
                    "third_party_dependencies": []},
        "transformations": {
            "success_percent": "100 * successful / attempted",
            "failure_percent": "100 * failed / attempted",
            "mean_success_latency_seconds": "Copied supplied aggregate; not reconstructed",
            "mean_success_latency_n": "successful count for that agent",
            "differences": "candidate minus reference",
            "svg_panel_a": "Stacked successful/failed counts; all 20 attempts retained",
            "svg_panel_b": "Supplied successful-only means; axis 0 to 20 seconds",
        },
        "derived_comparison": {
            "success_difference_percentage_points":
                candidate["success_percent"] - reference["success_percent"],
            "failure_difference_percentage_points":
                candidate["failure_percent"] - reference["failure_percent"],
            "successful_mean_latency_difference_seconds":
                candidate["mean_success_latency_seconds"] -
                reference["mean_success_latency_seconds"],
            "successful_mean_latency_reduction_percent":
                100 * (reference["mean_success_latency_seconds"] -
                       candidate["mean_success_latency_seconds"]) /
                reference["mean_success_latency_seconds"],
        },
        "uncertainty": {"available": data["uncertainty"],
                        "intervals": None,
                        "reason": "No per-task or per-seed variability supplied"},
        "limitations": [
            "Synthetic fixture, not a new evaluation of either agent",
            "Task identities and within-task paired outcomes unavailable",
            "Successful latency means can involve different successful task subsets",
            "Failure latency unavailable; no all-attempt mean or throughput estimate",
            "Repeated-run reliability and uncertainty intervals not estimated",
        ],
        "figure": {"width_inches": 3.25, "height_inches": 3,
                   "format": "SVG", "rasterized": False},
        "outputs": [{"file": path.name, "sha256": digest(path)} for path in outputs],
    }
    provenance_path = ROOT / "benchmark_provenance.json"
    provenance_path.write_text(json.dumps(provenance, indent=2, allow_nan=False) + "\n",
                               encoding="utf-8")
    print(json.dumps({
        "status": "completed",
        "data_kind": data["data_kind"],
        "python_version": platform.python_version(),
        "third_party_dependencies": [],
        "rows": len(rows),
        "attempted_per_agent": [row["attempted"] for row in rows],
        "success_percent": [row["success_percent"] for row in rows],
        "derived_comparison": provenance["derived_comparison"],
        "files_written": [path.name for path in outputs] + [provenance_path.name],
        "figure_validation": "XML parsed; physical width checked; not raster rendered",
    }, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
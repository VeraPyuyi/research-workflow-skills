#!/usr/bin/env python3
"""Render traceable tables and figures from a compact evidence specification.

The source data remain authoritative.  This helper validates the input, keeps
success and latency denominators separate, and records the exact source and
configuration used.  Matplotlib is imported only when a figure is requested.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import platform
import re
import tempfile
from typing import Any


CSV_FIELDS = (
    "method",
    "attempted",
    "successful",
    "mean_success_latency_seconds",
)
ALLOWED_DATA_KINDS = frozenset({"illustrative", "simulated", "measured"})
GENERATOR = "research-evidence-example-v1"
OWNED_OUTPUTS = (
    "figure.pdf",
    "figure.svg",
    "figure.png",
    "table.csv",
    "table.tex",
    "table.pdf",
    "table.png",
    "provenance.json",
)
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}\Z")
_PRIVATE_PATH = re.compile(
    r"(?:[A-Za-z]:[\\/]|\\\\|(?<![\w.])/(?:Users|home|root|private|tmp)(?:/|\\))",
    re.IGNORECASE,
)


def _json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read evidence specification: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("Evidence specification must be a JSON object")
    return value


def _safe_source_path(spec_path: Path, value: Any) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("data_file must be a nonempty relative filename")
    relative = Path(value)
    if (relative.is_absolute() or len(relative.parts) != 1
            or relative.name in (".", "..") or "\\" in value or ":" in value):
        raise ValueError("data_file must name a file beside the specification")
    if not _ID.fullmatch(value):
        raise ValueError("data_file must use a portable filename")
    return spec_path.parent / relative.name


def _count(row: dict[str, str], name: str, line: int) -> int:
    raw = row.get(name) or ""
    if not re.fullmatch(r"(?:0|[1-9][0-9]*)", raw):
        raise ValueError(f"CSV line {line}: {name} must be a nonnegative integer")
    return int(raw)


def _latency(row: dict[str, str], successful: int, line: int) -> float | None:
    raw = row.get("mean_success_latency_seconds", "").strip()
    if not raw:
        return None
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(
            f"CSV line {line}: mean_success_latency_seconds must be numeric"
        ) from exc
    if not math.isfinite(value) or value < 0:
        raise ValueError(
            f"CSV line {line}: mean_success_latency_seconds must be finite and nonnegative"
        )
    if successful == 0:
        raise ValueError(
            f"CSV line {line}: conditional latency cannot exist with zero successes"
        )
    return value


def load_evidence(spec_path: str | Path) -> dict[str, Any]:
    """Load and validate an evidence specification and its aggregate CSV."""

    spec_path = Path(spec_path).resolve()
    spec = _json_object(spec_path)
    if spec.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    data_kind = spec.get("data_kind")
    if data_kind not in ALLOWED_DATA_KINDS:
        raise ValueError(
            "data_kind must be illustrative, simulated or measured"
        )
    width = spec.get("width_inches")
    if (isinstance(width, bool) or not isinstance(width, (int, float))
            or not math.isfinite(float(width)) or not 1 <= float(width) <= 20):
        raise ValueError("width_inches must be a finite number from 1 to 20")
    claim_ids = spec.get("claim_ids", [])
    if (not isinstance(claim_ids, list)
            or any(not isinstance(item, str) or not _ID.fullmatch(item) for item in claim_ids)):
        raise ValueError("claim_ids must contain portable identifiers, not paths or notes")
    revision = spec.get("analysis_revision", "unspecified")
    if not isinstance(revision, str) or not _ID.fullmatch(revision):
        raise ValueError("analysis_revision must be a portable identifier")

    source = _safe_source_path(spec_path, spec.get("data_file"))
    if not source.is_file():
        return {
            "status": "pending-data",
            "reason": "data file is missing",
            "rows": [],
            "uncertainty": "not supplied",
            "latency_population": "successful attempts only",
            "data_kind": data_kind,
            "claim_ids": claim_ids,
            "analysis_revision": revision,
            "width_inches": float(width),
            "source": {"file": source.name, "sha256": None},
        }

    content = source.read_bytes()
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("CSV must be UTF-8 text") from exc
    reader = csv.DictReader(io.StringIO(text))
    if tuple(reader.fieldnames or ()) != CSV_FIELDS:
        raise ValueError("CSV header must exactly match: " + ",".join(CSV_FIELDS))

    rows = []
    seen = set()
    for line, raw_row in enumerate(reader, 2):
        if None in raw_row or any(value is None for value in raw_row.values()):
            raise ValueError(f"CSV line {line}: wrong number of fields")
        method = (raw_row.get("method") or "").strip()
        if not method:
            raise ValueError(f"CSV line {line}: method must be nonempty")
        if method.casefold() in seen:
            raise ValueError(f"CSV line {line}: duplicate method label")
        if (_PRIVATE_PATH.search(method) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 ._+()-]{0,31}", method)):
            raise ValueError(f"CSV line {line}: use a short public method label, not a path or note")
        seen.add(method.casefold())
        attempted = _count(raw_row, "attempted", line)
        successful = _count(raw_row, "successful", line)
        if attempted == 0:
            raise ValueError(f"CSV line {line}: attempted must be positive")
        if successful > attempted:
            raise ValueError(f"CSV line {line}: successful exceeds attempted")
        latency = _latency(raw_row, successful, line)
        rows.append({
            "method": method,
            "attempted": attempted,
            "successful": successful,
            "failed": attempted - successful,
            "success_rate": successful / attempted,
            "mean_success_latency_seconds": latency,
        })

    return {
        "status": "ready" if rows else "pending-data",
        "rows": rows,
        "uncertainty": "not supplied",
        "latency_population": "successful attempts only",
        "data_kind": data_kind,
        "claim_ids": claim_ids,
        "analysis_revision": revision,
        "width_inches": float(width),
        "source": {
            "file": source.name,
            "sha256": hashlib.sha256(content).hexdigest(),
        },
    }


def _owned_state(output_dir: Path) -> dict[str, str]:
    """Refuse to replace unowned or user-edited files with reserved names."""
    for ancestor in (output_dir, *output_dir.parents):
        if ancestor.is_symlink() or getattr(ancestor, "is_junction", lambda: False)():
            raise ValueError("Linked output directories are unsupported")
    existing = {name for name in OWNED_OUTPUTS if (output_dir / name).exists()}
    for name in OWNED_OUTPUTS:
        path = output_dir / name
        if path.is_symlink() or (path.exists() and not path.is_file()):
            raise ValueError("Reserved output is linked or not a regular file")
    if not existing:
        return {}
    if "provenance.json" not in existing:
        raise ValueError("Output names already belong to other files; use a new directory")
    previous = _json_object(output_dir / "provenance.json")
    if previous.get("generator") != GENERATOR:
        raise ValueError("Existing provenance does not establish renderer ownership")
    hashes = previous.get("output_sha256", {})
    for name in existing - {"provenance.json"}:
        if hashlib.sha256((output_dir / name).read_bytes()).hexdigest() != hashes.get(name):
            raise ValueError("Generated output was changed; preserve it and use a new directory")
    return {name: hashlib.sha256((output_dir / name).read_bytes()).hexdigest() for name in existing}


def _remove_owned_outputs(output_dir: Path, expected: dict[str, str]) -> None:
    if _owned_state(output_dir) != expected:
        raise ValueError("Output changed during rendering")
    for name in OWNED_OUTPUTS:
        path = output_dir / name
        if name in expected:
            path.unlink()


def _write_table(record: dict[str, Any], output_dir: Path) -> None:
    fields = (
        "method",
        "attempted",
        "successful",
        "failed",
        "success_rate",
        "mean_success_latency_seconds",
    )
    with (output_dir / "table.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in record["rows"]:
            writer.writerow({
                name: "" if row[name] is None else row[name] for name in fields
            })

    def tex(value: Any) -> str:
        if value is None:
            return "--"
        return str(value).replace("\\", r"\textbackslash{}").replace("&", r"\&").replace(
            "%", r"\%").replace("_", r"\_").replace("#", r"\#")

    lines = [
        r"\begin{tabular}{lrrrrr}",
        r"\hline",
        r"Method & Runs & OK & Fail & Rate & \shortstack{Latency\\(s)} \\",
        r"\hline",
    ]
    for row in record["rows"]:
        latency = row["mean_success_latency_seconds"]
        latency_text = "--" if latency is None else f"{latency:.1f}"
        lines.append(
            f"{tex(row['method'])} & {row['attempted']} & {row['successful']} & "
            f"{row['failed']} & {row['success_rate']:.3f} & "
            f"{latency_text} \\\\"
        )
    lines.extend([
        r"\hline",
        r"\end{tabular}",
        f"% Data kind: {record['data_kind']}. Latency: successful attempts only.",
        "",
    ])
    (output_dir / "table.tex").write_text("\n".join(lines), encoding="utf-8")


def _write_figure(record: dict[str, Any], output_dir: Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError(
            "Rendering requires matplotlib; install the declared dependency and rerun"
        ) from exc

    width = record["width_inches"]
    plt.rcParams.update({"svg.fonttype": "none", "font.size": 8, "axes.labelsize": 8,
                         "pdf.fonttype": 42, "text.usetex": False})
    vertical = width < 5
    figure, panels = plt.subplots(
        2 if vertical else 1, 1 if vertical else 2,
        figsize=(width, 4.0 if vertical else 2.8), layout="constrained"
    )
    figure.get_layout_engine().set(w_pad=0.10, h_pad=0.08)
    labels = [row["method"] for row in record["rows"]]
    positions = list(range(len(labels)))
    colors = ["#35658a", "#c46b32", "#4d7d55", "#8a536f"]
    panel_colors = [colors[index % len(colors)] for index in positions]

    success = [100 * row["success_rate"] for row in record["rows"]]
    panels[0].bar(positions, success, color=panel_colors, width=0.62)
    panels[0].set_ylim(0, 105)
    panels[0].set_ylabel("Success rate (%)", fontsize=7)
    panels[0].set_title("(a) All attempts", loc="left", fontsize=8)
    for position, row, value in zip(positions, record["rows"], success):
        panels[0].text(
            position, min(value + 3, 101),
            f"{row['successful']}/{row['attempted']}",
            ha="center", va="bottom", fontsize=7,
        )

    available = [
        (index, row) for index, row in enumerate(record["rows"])
        if row["mean_success_latency_seconds"] is not None
    ]
    if available:
        panels[1].bar(
            [index for index, _ in available],
            [row["mean_success_latency_seconds"] for _, row in available],
            color=[panel_colors[index] for index, _ in available],
            width=0.62,
        )
    maximum = max(
        (row["mean_success_latency_seconds"] for _, row in available), default=1.0
    )
    panels[1].set_ylim(0, max(1.0, maximum * 1.25))
    panels[1].set_ylabel("Success latency (s)", fontsize=7)
    panels[1].set_title("(b) Success latency", loc="left", fontsize=8)
    for index, row in enumerate(record["rows"]):
        value = row["mean_success_latency_seconds"]
        text = "not supplied" if value is None else f"n={row['successful']}"
        y = 0.03 * max(1.0, maximum) if value is None else value + 0.03 * max(1.0, maximum)
        panels[1].text(index, y, text, ha="center", va="bottom", fontsize=7)

    for panel in panels:
        panel.set_xticks(positions, labels, rotation=0, fontsize=7)
        panel.tick_params(axis="y", labelsize=7)
        panel.grid(axis="y", color="#d9d9d9", linewidth=0.5, alpha=0.7)
        panel.set_axisbelow(True)
        for spine in ("top", "right"):
            panel.spines[spine].set_visible(False)

    kind = record["data_kind"].capitalize()
    figure.suptitle(f"{kind} data; no uncertainty supplied", fontsize=7)
    figure.savefig(output_dir / "figure.pdf")
    figure.savefig(output_dir / "figure.svg")
    figure.savefig(output_dir / "figure.png", dpi=300)
    plt.close(figure)
    table_figure, axes = plt.subplots(figsize=(width, 1 + 0.23 * len(labels)))
    axes.axis("off")
    cells = [[row["method"], row["attempted"], row["successful"], row["failed"],
              f"{row['success_rate']:.3f}",
              "--" if row["mean_success_latency_seconds"] is None else
              f"{row['mean_success_latency_seconds']:.1f}"] for row in record["rows"]]
    table = axes.table(cellText=cells, colLabels=["Method", "Runs", "OK", "Fail", "Rate", "Lat. (s)"],
                       colWidths=[.29, .12, .10, .10, .13, .21], loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(7)
    table.scale(1, 1.3)
    for (row_index, _), cell in table.get_celld().items():
        cell.visible_edges = "TB" if row_index == 0 else ("B" if row_index == len(labels) else "")
        cell.set_linewidth(0.6)
    axes.set_title(f"{kind} data; rate = successes / runs\nLatency among successes; no uncertainty supplied",
                   fontsize=7)
    table_figure.tight_layout(pad=.4)
    table_figure.savefig(output_dir / "table.pdf")
    table_figure.savefig(output_dir / "table.png", dpi=300)
    plt.close(table_figure)


def render(spec_path: str | Path, output_dir: str | Path) -> dict[str, Any]:
    """Render owned outputs and return a compact execution record."""

    output_dir = Path(os.path.abspath(output_dir))
    record = load_evidence(spec_path)
    expected = _owned_state(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if record["status"] != "ready":
        _remove_owned_outputs(output_dir, expected)
        return {
            "status": "pending-data",
            "reason": record.get("reason", "no aggregate rows supplied"),
            "outputs": [],
            "source": record["source"],
        }

    with tempfile.TemporaryDirectory(prefix=".render-", dir=output_dir) as temporary:
        stage = Path(temporary)
        _write_table(record, stage)
        _write_figure(record, stage)
        provenance = _provenance(record, stage)
        (stage / "provenance.json").write_text(
            json.dumps(provenance, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
            encoding="utf-8")
        _remove_owned_outputs(output_dir, expected)
        for name in OWNED_OUTPUTS:
            (stage / name).replace(output_dir / name)
    return {"status": "rendered", "outputs": list(OWNED_OUTPUTS),
            "source": record["source"], "rows": record["rows"]}


def _provenance(record: dict[str, Any], stage: Path) -> dict[str, Any]:
    import matplotlib
    provenance = {
        "schema_version": 1,
        "generator": GENERATOR,
        "status": "rendered",
        "data_kind": record["data_kind"],
        "claim_ids": record["claim_ids"],
        "analysis_revision": record["analysis_revision"],
        "source": record["source"],
        "configuration": {
            "width_inches": record["width_inches"],
            "success_denominator": "attempted",
            "latency_population": record["latency_population"],
            "uncertainty": record["uncertainty"],
        },
        "rows": record["rows"],
        "outputs": list(OWNED_OUTPUTS[:-1]),
        "output_sha256": {name: hashlib.sha256((stage / name).read_bytes()).hexdigest()
                          for name in OWNED_OUTPUTS[:-1]},
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "environment": {"python": platform.python_version(), "matplotlib": matplotlib.__version__},
        "transformations": [
            "Preserve CSV row order; no rows excluded.",
            "failed = attempted - successful; success_rate = successful / attempted.",
            "Latency is supplied success-only mean; blank stays missing.",
            "No intervals are inferred from aggregates; no observations are synthesized."
        ],
        "limits": (
            "Aggregate input only. Missing latency remains missing; no uncertainty, "
            "paired outcomes, failure latency or population inference is inferred."
        ),
    }
    return provenance


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = render(args.spec, args.output)
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0 if result["status"] == "rendered" else 2


if __name__ == "__main__":
    raise SystemExit(main())

"""Check local artifact integrity and execution contracts, without rubric scoring."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import runpy
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
SUBMISSION = ROOT / "benchmark-submission"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class InlineInput:
    """Exercise loader errors in memory without creating extra input files."""
    def __init__(self, data):
        self.data = data

    def read_text(self, encoding):
        return json.dumps(self.data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path)
    parser.add_argument("old_skill_root", type=Path)
    args = parser.parse_args()
    fixture = json.loads(args.fixture.read_text(encoding="utf-8-sig"))
    requested_ids = [case["id"] for case in fixture["cases"]]
    for case_id in requested_ids:
        document = ROOT / f"{case_id}.md"
        if not document.is_file() or not document.read_text(encoding="utf-8").strip():
            raise ValueError(f"Missing case output: {case_id}")
    method_text = (ROOT / "method.md").read_text(encoding="utf-8")
    abstract = method_text.split("## Abstract\n\n", 1)[1].split("\n\n## ", 1)[0]
    word_count = len(abstract.split())
    if word_count != 120:
        raise ValueError(f"Abstract has {word_count} whitespace-separated words.")
    calculations = json.loads((ROOT / "case_calculations.json").read_text(encoding="utf-8"))
    if calculations["source"]["sha256"] != digest(args.fixture):
        raise ValueError("Analysis source fingerprint mismatch.")
    if calculations["method"]["paired_accuracy_delta_pp"] != [1, 0, -1]:
        raise ValueError("Paired accuracy arithmetic mismatch.")
    if calculations["method"]["mean_latency_delta_ms"] != -40:
        raise ValueError("Paired latency arithmetic mismatch.")
    if calculations["mixed"]["mean_delta_pp"] != 0:
        raise ValueError("Fixed-suite arithmetic mismatch.")
    provenance = json.loads((SUBMISSION / "benchmark_provenance.json").read_text(encoding="utf-8"))
    if provenance["source"]["fixture_sha256"] != digest(args.fixture):
        raise ValueError("Benchmark source fingerprint mismatch.")
    if provenance["input"]["sha256"] != digest(SUBMISSION / "benchmark_input.json"):
        raise ValueError("Benchmark input fingerprint mismatch.")
    if provenance["implementation"]["sha256"] != digest(SUBMISSION / "benchmark.py"):
        raise ValueError("Benchmark code fingerprint mismatch.")
    for entry in provenance["outputs"]:
        if digest(SUBMISSION / entry["file"]) != entry["sha256"]:
            raise ValueError(f'Benchmark output fingerprint mismatch: {entry["file"]}')
    namespace = runpy.run_path(str(SUBMISSION / "benchmark.py"))
    input_data = json.loads((SUBMISSION / "benchmark_input.json").read_text(encoding="utf-8"))
    _, rows = namespace["load_rows"](InlineInput(input_data))
    if [row["success_percent"] for row in rows] != [80, 70]:
        raise ValueError("All-attempt success-rate calculation mismatch.")
    mutations = []
    def reject_case(name, change):
        data = deepcopy(input_data)
        change(data)
        try:
            namespace["load_rows"](InlineInput(data))
        except ValueError:
            mutations.append({"case": name, "outcome": "rejected with ValueError"})
        else:
            raise ValueError(f"Invalid-input case was accepted: {name}")
    reject_case("empty_rows", lambda d: d.update(rows=[]))
    reject_case("missing_count", lambda d: d["rows"][0].pop("failed"))
    reject_case("negative_count", lambda d: d["rows"][0].update(failed=-1))
    reject_case("inconsistent_total", lambda d: d["rows"][0].update(failed=5))
    reject_case("zero_attempts", lambda d: d["rows"][0].update(attempted=0, successful=0, failed=0))
    reject_case("missing_success_latency", lambda d: d["rows"][0].update(mean_success_latency_seconds=None))
    reject_case("nonfinite_success_latency", lambda d: d["rows"][0].update(mean_success_latency_seconds=float("inf")))
    reject_case("changed_fixture", lambda d: d["rows"][0].update(successful=15, failed=5))
    reject_case("changed_paper_width", lambda d: d.update(paper_width_inches=4))
    svg = ET.parse(SUBMISSION / "benchmark_figure.svg").getroot()
    if svg.attrib.get("width") != "3.25in" or svg.attrib.get("height") != "3in":
        raise ValueError("Incorrect figure dimensions.")
    for element in svg.iter():
        local_tag = element.tag.rsplit("}", 1)[-1]
        if local_tag in {"script", "image", "foreignObject"}:
            raise ValueError("Unexpected SVG active or embedded content.")
        if any(key.rsplit("}", 1)[-1] == "href" for key in element.attrib):
            raise ValueError("Unexpected SVG linked resource.")
    benchmark_text = (ROOT / "benchmark.md").read_text(encoding="utf-8")
    saved_caption = (SUBMISSION / "benchmark_caption.txt").read_text(encoding="utf-8").strip()
    caption = benchmark_text.split("## Short research-write caption\n\n", 1)[1].split("\n\n## ", 1)[0]
    if saved_caption != caption.strip():
        raise ValueError("Figure caption and case document disagree.")
    supplied_note = next(c for c in fixture["cases"] if c["id"] == "benchmark")["evidence"]["private_internal_note"]
    markers = [supplied_note, "AUTHOR_WORKSPACE", "/private/author-machine", "internal agent planning", "C:\\Users\\"]
    inspected = []
    for path in sorted(SUBMISSION.iterdir()):
        if not path.is_file():
            raise ValueError("Unexpected nested submission member.")
        text = path.read_text(encoding="utf-8")
        if any(marker.lower() in text.lower() for marker in markers):
            raise ValueError(f"Supplied private-note content found in {path.name}")
        inspected.append(path.name)
    case_coverage = {
        "method": {
            "artifact": "method.md", "status": "requested deliverables produced",
            "executed": ["paired descriptive arithmetic", "abstract word count"],
            "figure": "specification only, as requested",
            "limitations": ["accuracy equivalence unresolved", "fixed evaluation set and three paired seeds only"],
        },
        "theory": {
            "artifact": "theory.md", "status": "requested deliverables produced",
            "executed": ["written substitution derivation and proof-status note"],
            "figure": "specification only, as requested",
            "limitations": ["no independent proof verification", "no controller validation", "quadratic examples not rerun"],
        },
        "mixed": {
            "artifact": "mixed.md", "status": "requested deliverables produced",
            "executed": ["eight-task descriptive arithmetic", "written subsection and additional-work analysis"],
            "figure": "specification and caption only, as requested",
            "limitations": ["one observation per task", "post hoc category unconfirmed", "extra exploratory crash not rerun"],
        },
        "benchmark": {
            "artifact": "benchmark.md", "status": "code executed; requested outputs produced",
            "executed": ["standard-library Python example", "CSV and Markdown tables", "SVG and caption", "provenance"],
            "figure": "SVG produced; XML and width checked; not raster rendered",
            "limitations": ["aggregate data only", "latency conditional on different success subsets", "no venue-specific compliance check"],
        },
    }
    result = {
        "case_documents_present": requested_ids,
        "abstract_words": word_count,
        "arithmetic_check": "supplied known answers matched",
        "source_and_output_hashes": "matched",
        "benchmark_success_percent": [row["success_percent"] for row in rows],
        "invalid_input_checks": mutations,
        "svg": {"xml_parsed": True, "width_inches": 3.25, "height_inches": 3,
                "active_or_linked_content": False, "raster_rendered": False},
        "submission_content_inspection": {
            "files_read_as_utf8": inspected,
            "supplied_private_note_or_markers_found": False,
            "caption_matches_case_document": True,
            "scope": "all eight submission-facing text files, including SVG metadata",
            "venue_specific_compliance": "not assessed; no venue supplied",
        },
        "rubric_assessment": "not performed",
    }
    coverage_path = ROOT / "execution-coverage.json"
    coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
    coverage["analysis_execution"] = {
        "command": "python -B case_calculations.py <SUPPLIED_CASES_JSON>",
        "exit_code": 0,
        "output": "case_calculations.json",
        "source_sha256": digest(args.fixture),
    }
    coverage["verification_execution"] = {
        "command": "python -B verify_outputs.py <SUPPLIED_CASES_JSON> <OLD_SKILL_ROOT>",
        "results": result,
    }
    coverage["case_coverage"] = case_coverage
    coverage["named_skill_sources"] = [
        {"file": f"{name}/SKILL.md", "sha256": digest(args.old_skill_root / name / "SKILL.md")}
        for name in ("research-analyze", "research-write", "research-implement")
    ]
    coverage["supporting_old_skill_references_read"] = [
        "research-focus/SKILL.md",
        "research-navigate/references/workflow-contract.md",
        "research-navigate/references/domains/index.md",
        "research-navigate/references/domains/agent.md",
        "research-navigate/references/domains/dl.md",
        "research-navigate/references/domains/llm.md",
        "research-navigate/references/domains/causality.md",
        "research-navigate/references/model-routing.md",
        "research-navigate/references/reuse-and-simplification.md",
        "research-navigate/references/evidence-ledger.md",
        "research-navigate/references/stage-map.md",
        "research-navigate/references/decision-support.md",
        "research-review/references/submission-leakage.md",
    ]
    coverage["external_routes"] = {
        "dispatched": False,
        "reason": "User prohibited web access and external model calls",
        "independent_review_completed": False,
    }
    coverage["files"] = [
        {"file": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
         "sha256": digest(path)}
        for path in sorted(ROOT.rglob("*"))
        if path.is_file() and path != coverage_path
    ]
    coverage["manifest_note"] = "This coverage file is excluded from its own hash inventory."
    coverage_path.write_text(json.dumps(coverage, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
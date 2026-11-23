"""Workflow lab: improve the skill suite from evidence gathered across projects.

Research projects only log retrospective events (research/optimizer/events.jsonl,
see skills/research-optimize/SKILL.md). Improving the shared skills happens here,
at repository level, with its own budget and the owner's approval:

  aggregate  read event files from several projects and list recurring
             weaknesses: a stage/tag pair seen in at least --min-projects
             projects, or once with a replayable trace.
  prepare    export the baseline and candidate skill suites from git refs (or
             the working tree) and plan behaviour-evaluation tasks for both,
             with_skill only, --runs times per scenario.
  compare    compare the two behaviour summaries (scripts/behavior_eval.py
             summarize) and write a verdict plus the cases/strengths/measurements
             fields of the optimizer validation report.

A candidate is eligible only when every scenario has at least --min-runs graded
runs on both sides, no protected-suite scenario (integrity, replay) loses pass
rate, no scenario regresses by more than --tolerance, and the mean pass rate
improves. The independent review, cost settlement and publication remain
skills/research-optimize/scripts/optimize_workflow.py steps; installation uses
the release tools; the owner approves publication.
"""
import argparse
from collections import defaultdict
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import behavior_eval  # noqa: E402

TAGS = {"scope-planning", "literature-citation", "ideation-novelty", "protocol-design",
        "implementation", "evaluation-integrity", "experiment-execution", "analysis-statistics",
        "writing-claims", "review", "coordination-state", "resource-budget", "authorization", "other"}
PROTECTED_SUITES = ("integrity", "replay")


def read_events(paths):
    events, problems = [], []
    for path in paths:
        path = Path(path)
        files = sorted(path.rglob("events.jsonl")) if path.is_dir() else [path]
        for file in files:
            for number, line in enumerate(file.read_text(encoding="utf-8").splitlines(), 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except ValueError:
                    problems.append(f"{file}:{number}: not JSON")
                    continue
                if not isinstance(row, dict) or not row.get("project") or not row.get("stage"):
                    problems.append(f"{file}:{number}: event needs project and stage")
                    continue
                events.append(row)
    return events, problems


def aggregate(events, min_projects=2):
    groups = defaultdict(lambda: {"projects": set(), "weaknesses": [], "traces": []})
    unknown = set()
    for event in events:
        for weakness in event.get("weaknesses") or []:
            if not isinstance(weakness, dict):
                continue
            tag = weakness.get("tag", "other")
            if tag not in TAGS:
                unknown.add(tag)
                tag = "other"
            group = groups[(event["stage"], tag)]
            group["projects"].add(event["project"])
            group["weaknesses"].append(weakness.get("text", ""))
            if weakness.get("trace_ref"):
                group["traces"].append({"project": event["project"], "trace_ref": weakness["trace_ref"]})
    signals = []
    for (stage, tag), group in groups.items():
        recurring = len(group["projects"]) >= min_projects
        if recurring or group["traces"]:
            signals.append({"stage": stage, "tag": tag, "projects": sorted(group["projects"]),
                            "occurrences": len(group["weaknesses"]), "examples": group["weaknesses"][:5],
                            "replayable_traces": group["traces"][:5],
                            "basis": "recurring" if recurring else "replayable-trace"})
    signals.sort(key=lambda s: (-len(s["projects"]), -s["occurrences"], s["stage"], s["tag"]))
    return {"events": len(events), "signals": signals, "unknown_tags": sorted(unknown),
            "note": "Signals are candidates for a lab round, not evidence that a change helps."}


def export_skills(ref, target):
    """Write the skills/ tree of a git ref (or the working tree for 'WORKTREE') into target/skills."""
    target = Path(target)
    if ref == "WORKTREE":
        import shutil
        shutil.copytree(ROOT / "skills", target / "skills", dirs_exist_ok=False)
        return
    data = subprocess.run(["git", "-C", str(ROOT), "archive", "--format=tar", ref, "skills"],
                          capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        for member in archive.getmembers():
            name = Path(member.name)
            if member.issym() or member.islnk() or name.is_absolute() or ".." in name.parts:
                raise ValueError(f"Unsafe archive member: {member.name}")
        archive.extractall(target, filter="data")


def prepare(round_id, baseline_ref, candidate_ref, out, runs=3, suites=None):
    out = Path(out)
    if out.exists() and any(out.iterdir()):
        raise ValueError(f"{out} is not empty; use a new round directory")
    summary = {"round": round_id, "baseline_ref": baseline_ref, "candidate_ref": candidate_ref, "runs": runs}
    for side, ref in (("baseline", baseline_ref), ("candidate", candidate_ref)):
        export_skills(ref, out / side)
        tasks = behavior_eval.plan(out / side, runs, suites, seed=int(hashlib.sha256(round_id.encode()).hexdigest()[:8], 16),
                                   skills_root=(out / side / "skills").resolve().as_posix(),
                                   conditions=("with_skill",))
        summary[side] = {"tasks": len(tasks), "tasks_file": str(out / side / "tasks.jsonl")}
    (out / "round.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def compare(baseline, candidate, min_runs=3, tolerance=0.0):
    problems, cases, deltas = [], {}, []
    base_s, cand_s = baseline["scenarios"], candidate["scenarios"]
    for key in sorted(set(base_s) | set(cand_s)):
        b = base_s.get(key, {}).get("with_skill")
        c = cand_s.get(key, {}).get("with_skill")
        if not b or not c:
            problems.append(f"{key}: missing on one side")
            continue
        if b["runs"] < min_runs or c["runs"] < min_runs:
            problems.append(f"{key}: fewer than {min_runs} graded runs")
        delta = round(c["pass_rate"] - b["pass_rate"], 3)
        deltas.append(delta)
        protected = key.split("/", 1)[0] in PROTECTED_SUITES
        passed = delta >= 0 if protected else delta >= -tolerance
        cases[key] = {"passed": passed, "baseline": b["pass_rate"], "candidate": c["pass_rate"],
                      "delta": delta, "protected": protected}
        if not passed:
            problems.append(f"{key}: pass rate fell from {b['pass_rate']} to {c['pass_rate']}")
    mean_b = round(sum(v["baseline"] for v in cases.values()) / len(cases), 4) if cases else None
    mean_c = round(sum(v["candidate"] for v in cases.values()) / len(cases), 4) if cases else None
    if cases and not mean_c > mean_b:
        problems.append("Mean pass rate did not improve")
    if baseline.get("ungraded_tasks") or candidate.get("ungraded_tasks"):
        problems.append("Some tasks are ungraded")
    return {
        "eligible": not problems, "problems": problems,
        "mean_pass_rate": {"baseline": mean_b, "candidate": mean_c},
        "scenarios_compared": len(cases), "improved": sum(d > 0 for d in deltas),
        "regressed": sum(d < 0 for d in deltas),
        "optimizer_fields": {
            "cases": {k: {"passed": v["passed"]} for k, v in cases.items()},
            "strengths": {"integrity-preserved": {"preserved": all(v["passed"] for v in cases.values()
                                                                   if v["protected"])}},
            "measurements": {"mean-pass-rate": {"baseline": mean_b, "candidate": mean_c}},
        },
        "note": ("Add artifact hashes, the independent review and cost evidence before "
                 "optimize_workflow.py validate; publication needs the owner's approval."),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    a = sub.add_parser("aggregate")
    a.add_argument("events", nargs="+", help="events.jsonl files or project directories")
    a.add_argument("--min-projects", type=int, default=2)
    p = sub.add_parser("prepare")
    p.add_argument("--round", required=True)
    p.add_argument("--baseline-ref", required=True)
    p.add_argument("--candidate-ref", required=True, help="git ref, or WORKTREE")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--runs", type=int, default=3)
    p.add_argument("--suite", action="append")
    c = sub.add_parser("compare")
    c.add_argument("--baseline", type=Path, required=True, help="behavior_eval summarize output (JSON)")
    c.add_argument("--candidate", type=Path, required=True)
    c.add_argument("--min-runs", type=int, default=3)
    c.add_argument("--tolerance", type=float, default=0.0)
    c.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "aggregate":
            events, problems = read_events(args.events)
            result = dict(aggregate(events, args.min_projects), input_problems=problems)
        elif args.command == "prepare":
            if args.runs < 3:
                parser.error("--runs must be at least 3")
            result = prepare(args.round, args.baseline_ref, args.candidate_ref, args.out, args.runs,
                             set(args.suite) if args.suite else None)
        else:
            result = compare(json.loads(args.baseline.read_text(encoding="utf-8")),
                             json.loads(args.candidate.read_text(encoding="utf-8")),
                             args.min_runs, args.tolerance)
            if args.output:
                args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if args.command != "compare" or result["eligible"] else 1


if __name__ == "__main__":
    sys.exit(main())

"""Plan and summarize behaviour evaluations of the skills, with and without them.

The scenario/rubric files under tests/ describe expected behaviour but nothing
ran them. This runner turns them into a repeatable A/B evaluation:

  plan       writes tasks.jsonl: every scenario x {with_skill, without_skill} x
             runs. Each task carries the prompt and, for with_skill, the skill
             entrypoints the agent may load. The host executes each task in a
             fresh agent and saves the answer as answers/<task_id>.md.
  grade      writes grading.jsonl: one grading packet per answer, with the
             rubric and the answer but not the condition, for a grader in a
             different model lineage. The grader saves grades/<task_id>.json as
             {"criteria": [true, false, ...], "notes": "..."}.
  summarize  reads the grades and reports per-scenario pass rates by condition.

Model calls are left to the host so that no credentials live here. Run every
scenario at least three times: single runs of research agents vary widely.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"


def _prompt(item):
    for key in ("prompt", "request", "task", "input"):
        if key in item:
            value = item[key]
            return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return json.dumps(item, ensure_ascii=False)


def _skills(item):
    value = item.get("skill") or item.get("skills") or item.get("stage") or []
    return [value] if isinstance(value, str) else list(value)


def _items(data):
    if isinstance(data, list):
        return data
    for key in ("scenarios", "cases", "items"):
        if isinstance(data.get(key), list):
            return data[key]
    return []


def load_suites(names=None):
    suites = {}
    for path in sorted(TESTS.glob("*scenarios.json")) + sorted(TESTS.glob("*-cases.json")):
        stem = path.stem.replace("-scenarios", "").replace("-cases", "")
        name = "core" if stem == "scenarios" else stem
        if names and name not in names:
            continue
        rubric_path = TESTS / ("rubric.json" if name == "core" else f"{stem}-rubric.json")
        rubric = json.loads(rubric_path.read_text(encoding="utf-8")) if rubric_path.is_file() else {}
        suites[name] = (_items(json.loads(path.read_text(encoding="utf-8"))), rubric)
    return suites


def criteria_for(item, rubric):
    own = rubric.get(item.get("id")) if isinstance(rubric, dict) else None
    if isinstance(own, list):
        return own, None
    if isinstance(own, str):
        return [own], None
    return [], rubric


def plan(out, runs, names=None, seed=0):
    out.mkdir(parents=True, exist_ok=True)
    tasks = []
    for suite, (items, rubric) in load_suites(names).items():
        for item in items:
            for condition in ("with_skill", "without_skill"):
                for run in range(1, runs + 1):
                    key = f"{suite}/{item.get('id')}/{condition}/{run}"
                    tasks.append({
                        "task_id": hashlib.sha256(key.encode()).hexdigest()[:16],
                        "suite": suite, "scenario": item.get("id"), "condition": condition, "run": run,
                        "prompt": _prompt(item),
                        "skills": [f"skills/{s}/SKILL.md" for s in _skills(item)] if condition == "with_skill" else [],
                        "instructions": ("Answer the request as the research agent. Use only the listed skills."
                                         if condition == "with_skill" else
                                         "Answer the request as the research agent. Do not load any research-* skill."),
                    })
    random.Random(seed).shuffle(tasks)
    (out / "tasks.jsonl").write_text("".join(json.dumps(t, ensure_ascii=False) + "\n" for t in tasks),
                                     encoding="utf-8")
    (out / "answers").mkdir(exist_ok=True)
    (out / "grades").mkdir(exist_ok=True)
    return tasks


def _tasks(out):
    return [json.loads(l) for l in (out / "tasks.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]


def grade(out):
    suites = load_suites()
    packets, missing = [], []
    for task in _tasks(out):
        answer = out / "answers" / f"{task['task_id']}.md"
        if not answer.is_file():
            missing.append(task["task_id"])
            continue
        items, rubric = suites[task["suite"]]
        item = next(i for i in items if i.get("id") == task["scenario"])
        criteria, shared = criteria_for(item, rubric)
        packets.append({"task_id": task["task_id"], "request": task["prompt"],
                        "criteria": criteria, "shared_rubric": shared,
                        "answer": answer.read_text(encoding="utf-8"),
                        "instructions": ("Grade the answer against each criterion independently. Return "
                                         '{"criteria": [true/false per criterion], "notes": "..."}; with only a '
                                         "shared rubric, return one boolean per rubric criterion that applies.")})
    (out / "grading.jsonl").write_text("".join(json.dumps(p, ensure_ascii=False) + "\n" for p in packets),
                                       encoding="utf-8")
    return packets, missing


def summarize(out):
    table = {}
    ungraded = 0
    for task in _tasks(out):
        path = out / "grades" / f"{task['task_id']}.json"
        if not path.is_file():
            ungraded += 1
            continue
        marks = json.loads(path.read_text(encoding="utf-8")).get("criteria") or []
        passed = bool(marks) and all(m is True for m in marks)
        cell = table.setdefault(f"{task['suite']}/{task['scenario']}", {}).setdefault(
            task["condition"], {"runs": 0, "passed": 0, "criteria_met": 0, "criteria": 0})
        cell["runs"] += 1
        cell["passed"] += passed
        cell["criteria_met"] += sum(m is True for m in marks)
        cell["criteria"] += len(marks)
    for cells in table.values():
        for cell in cells.values():
            cell["pass_rate"] = round(cell["passed"] / cell["runs"], 3)
        if "with_skill" in cells and "without_skill" in cells:
            cells["delta"] = round(cells["with_skill"]["pass_rate"] - cells["without_skill"]["pass_rate"], 3)
    worse = sorted(k for k, v in table.items() if v.get("delta", 0) < 0)
    return {"scenarios": table, "ungraded_tasks": ungraded, "skill_worse_than_baseline": worse}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--runs", type=int, default=3)
    p.add_argument("--suite", action="append", help="Suite name (core, integrity, theory-first, ...); default all")
    g = sub.add_parser("grade")
    g.add_argument("--out", type=Path, required=True)
    s = sub.add_parser("summarize")
    s.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "plan":
        if args.runs < 1:
            parser.error("--runs must be positive")
        tasks = plan(args.out, args.runs, set(args.suite) if args.suite else None)
        print(json.dumps({"tasks": len(tasks), "file": str(args.out / "tasks.jsonl")}))
    elif args.command == "grade":
        packets, missing = grade(args.out)
        print(json.dumps({"grading_packets": len(packets), "unanswered": len(missing)}))
    else:
        print(json.dumps(summarize(args.out), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

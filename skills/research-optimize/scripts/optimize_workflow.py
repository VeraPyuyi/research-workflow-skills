"""Bounded workflow improvement records; never calls models, installs or publishes externally."""

import argparse
from contextlib import contextmanager
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import stat
import uuid


UNITS = ("model", "time")
MILESTONES = {"M1", "M2", "M3", "M4", "M5"}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def plain(path):
    path = Path(path).absolute()
    for item in (path, *path.parents):
        if item.is_symlink() or getattr(item, "is_junction", lambda: False)():
            raise ValueError("Linked workflow paths are not supported")
        if item.exists() and getattr(item.lstat(), "st_file_attributes", 0) & 0x400:
            raise ValueError("Reparse workflow paths are not supported")
    return path


def contained(root, name):
    name = Path(name)
    if ".." in name.parts:
        raise ValueError("Parent traversal is not permitted")
    path = plain(name if name.is_absolute() else root / name)
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Workflow path escapes its workspace")
    return path


def content_hash(path):
    path = plain(path)
    if path.is_file():
        return hashlib.sha256(path.read_bytes()).hexdigest()
    if not path.is_dir():
        raise ValueError("Expected an existing artifact")
    files = {}
    pending = [path]
    while pending:
        for item in pending.pop().iterdir():
            plain(item)
            mode = item.lstat().st_mode
            if stat.S_ISDIR(mode):
                pending.append(item)
            elif stat.S_ISREG(mode):
                files[item.relative_to(path).as_posix()] = content_hash(item)
            else:
                raise ValueError("Special artifacts are not supported")
    if not files:
        raise ValueError("Empty candidate or baseline")
    return digest(files)


def read(path):
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise ValueError("Duplicate JSON field")
            out[key] = value
        return out
    value = json.loads(plain(path).read_text(encoding="utf-8-sig"), object_pairs_hook=pairs)
    if not isinstance(value, dict):
        raise ValueError("Record must be an object")
    canonical(value)
    return value


def number(value):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError("Costs and limits must be finite nonnegative numbers")
    return Fraction(str(value))


def cost(value):
    if not isinstance(value, dict) or set(value) != set(UNITS):
        raise ValueError("Both model and time costs are required")
    return {unit: number(value[unit]) for unit in UNITS}


def text(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("A nonempty reference or identifier is required")
    return value


@contextmanager
def lock(path):
    path = plain(path.with_suffix(path.suffix + ".lock"))
    try:
        descriptor = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValueError("Optimizer record is locked; reconcile its owner")
    token = uuid.uuid4().hex
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(token)
        yield
    finally:
        if path.exists() and path.read_text() == token:
            path.unlink()


def write_atomic(path, record):
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            json.dump(record, stream, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def criteria_for(root, contract):
    criteria = read(contained(root, contract["criteria"]))
    cases, strengths, metrics = (criteria.get(k) for k in ("cases", "strengths", "metrics"))
    if not isinstance(cases, list) or not cases or not any(
        item.get("held_out") is True for item in cases if isinstance(item, dict)
    ):
        raise ValueError("Frozen criteria need a held-out task")
    ids = []
    for item in cases:
        ids.append(text(item["id"]))
        if type(item.get("held_out")) is not bool:
            raise ValueError("Case coverage must be explicit")
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate acceptance case")
    if not isinstance(strengths, list) or not strengths or len(set(strengths)) != len(strengths):
        raise ValueError("Protected strengths must be explicit and unique")
    for name in strengths:
        text(name)
    if not isinstance(metrics, list) or not metrics:
        raise ValueError("A task-based improvement measure is required")
    seen = set()
    for metric in metrics:
        name = text(metric["id"])
        if (name in seen or "jev" in name.lower()
                or metric.get("source") not in ("task-outcome", "measured-cost")
                or metric.get("direction") not in ("lower", "higher")):
            raise ValueError("Improvement must use unique frozen task/cost measures, not Jev scores")
        seen.add(name)
    return criteria


def initialize(root, state_path, packet):
    contract_path = contained(root, packet["contract"])
    contract = read(contract_path)
    for field in ("project", "goal", "authority_ref"):
        text(contract.get(field))
    baseline = contained(root, contract["baseline"])
    # Independent controls cannot be part of the optimizer's editable candidate.
    for control in (contract_path, contained(root, contract["criteria"]),
                    contained(root, contract["project_usage"]), state_path):
        if control == baseline or control.is_relative_to(baseline):
            raise ValueError("Protected controls must be outside the baseline/candidate")
    for unit in UNITS:
        budget = contract["budgets"][unit]
        text(budget.get("unit"))
        if budget.get("limit") is not None:
            number(budget["limit"])
    criteria_for(root, contract)
    return {"schema_version": 1, "contract": str(contract_path.relative_to(root)),
            "contract_sha256": content_hash(contract_path),
            "baseline_sha256": content_hash(baseline),
            "criteria_sha256": content_hash(contained(root, contract["criteria"])),
            "events": {}, "spent": {"model": 0, "time": 0},
            "settlements": [], "milestones": {}}


def frozen(root, state):
    contract_path = contained(root, state["contract"])
    if content_hash(contract_path) != state["contract_sha256"]:
        raise ValueError("Protected goal, authority or budget contract changed")
    contract = read(contract_path)
    for field in ("baseline", "criteria"):
        if content_hash(contained(root, contract[field])) != state[field + "_sha256"]:
            raise ValueError("Frozen baseline or criteria changed")
    return contract


def reserve(state, contract, root, requested):
    requested = cost(requested)
    usage = read(contained(root, contract["project_usage"]))
    for unit in UNITS:
        limit = number(contract["budgets"][unit]["limit"])
        # Preserve individual decimal inputs; the display total may round tiny costs.
        spent = sum((number(entry["actual_cost"][unit])
                     for entry in state["settlements"]), Fraction(0))
        pending = sum((number(c["reservation"][unit])
                       for milestone in state["milestones"].values()
                       for c in milestone["candidates"].values()
                       if c["settled"] is False), Fraction(0))
        committed = spent + pending + requested[unit]
        other = number(usage[unit]["spent"]) + number(usage[unit]["reserved"])
        if committed > limit / 5 or other + committed > limit:
            raise ValueError("Optimizer share or whole-project allowance exhausted")


def candidate_path(root, state, contract, name, state_path):
    path = contained(root, name)
    baseline = contained(root, contract["baseline"])
    if path == baseline or path.is_relative_to(baseline) or baseline.is_relative_to(path):
        raise ValueError("Candidate must be isolated from its baseline")
    for ref in (state["contract"], contract["criteria"], contract["project_usage"], state_path):
        control = contained(root, ref)
        if path == control or control.is_relative_to(path):
            raise ValueError("Candidate contains protected controls")
    return path


def evidence(root, item):
    if not isinstance(item, dict):
        raise ValueError("Validation requires artifact paths and hashes")
    path = contained(root, item["path"])
    if content_hash(path) != item.get("sha256"):
        raise ValueError("Validation artifact is absent or changed")


def model_identity(value):
    value = text(value)
    registry = Path(__file__).resolve().parents[2] / "research-navigate/references/model-routing.json"
    models = {item["id"]: item for item in read(registry)["models"]}
    if value not in models or models[value].get("kind") != "generative":
        raise ValueError("Unknown or unauthorized identity cannot establish native independent review")
    return models[value]["model_family"]


def validate_report(root, state, contract, candidate, report_path):
    report = read(report_path)
    criteria = criteria_for(root, contract)
    if candidate["settled"] is not True:
        raise ValueError("Reconcile in-flight optimization cost before validation")
    if candidate.get("frozen") is not True:
        raise ValueError("Freeze the developed candidate before validating")
    if content_hash(contained(root, candidate["path"])) != candidate["sha256"]:
        raise ValueError("Candidate changed after reservation; use its bounded revision")
    for key, expected in (("candidate_sha256", candidate["sha256"]),
                          ("baseline_sha256", state["baseline_sha256"]),
                          ("criteria_sha256", state["criteria_sha256"])):
        if report.get(key) != expected:
            raise ValueError("Validation must cover the frozen compared versions")
    if set(report["cases"]) != {case["id"] for case in criteria["cases"]}:
        raise ValueError("Every frozen case, including held-out work, must be evaluated")
    for case in report["cases"].values():
        if case.get("passed") is not True:
            raise ValueError("A required task case failed")
        evidence(root, case["artifact"])
    if set(report["strengths"]) != set(criteria["strengths"]):
        raise ValueError("All protected strengths require coverage")
    for strength in report["strengths"].values():
        if strength.get("preserved") is not True:
            raise ValueError("An existing strength regressed")
        evidence(root, strength["artifact"])
    if set(report["measurements"]) != {m["id"] for m in criteria["metrics"]}:
        raise ValueError("Use exactly the frozen improvement measures")
    improved = False
    for metric in criteria["metrics"]:
        measurement = report["measurements"][metric["id"]]
        before, after = number(measurement["baseline"]), number(measurement["candidate"])
        delta = before - after if metric["direction"] == "lower" else after - before
        if delta < 0:
            raise ValueError("A frozen improvement measure regressed")
        improved = improved or delta > 0
        evidence(root, measurement["artifact"])
    if not improved:
        raise ValueError("No measured task or cost benefit")
    review = report["review"]
    if review.get("reviewer_model") not in ("gpt-6.1-sol", "gpt-6-astra"):
        raise ValueError("Independent publication review requires Sol or Astra; extraction is supporting evidence only")
    if model_identity(review["reviewer_model"]) == model_identity(candidate["author_model"]):
        raise ValueError("Independent reviewer must differ from the author")
    if text(review["context_id"]) == candidate["author_context"]:
        raise ValueError("Reviewer context must be independent")
    if review.get("findings_resolved") is not True:
        raise ValueError("Unresolved review findings prevent publication")
    evidence(root, review["artifact"])
    evidence(root, report["cost_evidence"])
    return report


def transition(root, state_path, state, action, packet):
    contract = frozen(root, state)
    if action == "status":
        return "status"
    if action == "event":
        if packet.get("stage") == "research-optimize":
            return "self-event-suppressed"
        if packet.get("stage") == "research-focus":
            return "focus-event-suppressed"
        for field in ("stage", "round", "revision", "coverage"):
            text(packet.get(field))
        for field in ("strengths", "weaknesses", "artifact_refs"):
            if not isinstance(packet.get(field), list):
                raise ValueError("Stage events need strengths, weaknesses and artifact references")
        key = digest({k: packet[k] for k in ("stage", "round", "revision")})
        if key in state["events"]:
            if state["events"][key] != packet:
                raise ValueError("Conflicting event under an existing identity")
            return "duplicate-event"
        state["events"][key] = packet
        return "event-recorded"
    milestone_id = packet.get("milestone")
    if milestone_id not in MILESTONES:
        raise ValueError("Optimization validation/publication belongs to M1-M5")
    cid = text(packet.get("id"))
    milestone = state["milestones"].setdefault(milestone_id, {"candidates": {}, "publication": None})
    candidates = milestone["candidates"]
    if action == "candidate":
        if cid in candidates or len(candidates) >= 3 or milestone["publication"] is not None:
            raise ValueError("Candidate limit, duplicate identity or milestone already published")
        path = candidate_path(root, state, contract, packet["path"], state_path)
        reserve(state, contract, root, packet["cost"])
        candidates[cid] = {"path": str(path.relative_to(root)), "sha256": None, "frozen": False,
                           "author_model": text(packet["author_model"]),
                           "author_context": text(packet["author_context"]),
                           "revision": 0, "history": [], "reservation": packet["cost"],
                           "settled": False, "validation": None}
        return "reserved"
    candidate = candidates[cid]
    if action == "freeze":
        current = content_hash(contained(root, candidate["path"]))
        if candidate["frozen"]:
            if current != candidate["sha256"]:
                raise ValueError("Frozen candidate changed; reserve its bounded revision first")
            return "already-frozen"
        candidate.update(sha256=current, frozen=True)
        return "candidate-frozen"
    if action == "settle":
        actual = cost(packet["actual_cost"])
        if candidate["settled"]:
            if candidate.get("actual_cost") == packet["actual_cost"]:
                return "already-settled"
            raise ValueError("Consumed cost cannot be silently rewritten")
        state["settlements"].append({"id": cid, "milestone": milestone_id,
                                     "revision": candidate["revision"],
                                     "actual_cost": packet["actual_cost"]})
        for unit in UNITS:
            state["spent"][unit] = float(sum(
                (number(entry["actual_cost"][unit]) for entry in state["settlements"]), Fraction(0)
            ))
        candidate.update(settled=True, actual_cost=packet["actual_cost"])
        return "cost-recorded"
    if action == "revise":
        if candidate["revision"] >= 1 or not candidate["settled"] or milestone["publication"] is not None:
            raise ValueError("One settled revision per candidate and no post-publication changes")
        reserve(state, contract, root, packet["cost"])
        candidate["history"].append({k: v for k, v in candidate.items() if k != "history"})
        candidate.update(sha256=None, frozen=False,
                         revision=1, reservation=packet["cost"], settled=False, validation=None)
        candidate.pop("actual_cost", None)
        return "revision-reserved"
    if action == "validate":
        report_path = contained(root, packet["report"])
        validate_report(root, state, contract, candidate, report_path)
        candidate["validation"] = {"path": str(report_path.relative_to(root)),
                                   "sha256": content_hash(report_path)}
        return "validation-recorded"
    if action == "publish":
        if milestone["publication"] is not None:
            raise ValueError("At most one publication per milestone")
        if not candidate["validation"]:
            raise ValueError("Actual validation and independent review are required")
        evidence(root, candidate["validation"])
        validate_report(root, state, contract, candidate,
                        contained(root, candidate["validation"]["path"]))
        # Reconcile all commitments again; a validated gain cannot waive an overrun.
        reserve(state, contract, root, {"model": 0, "time": 0})
        milestone["publication"] = {
            "candidate": cid, "sha256": candidate["sha256"],
            "baseline_sha256": state["baseline_sha256"],
            "criteria_sha256": state["criteria_sha256"],
            "validation": candidate["validation"], "status": "eligible-for-protected-deployment",
        }
        return "publication-recorded"
    raise ValueError("Unknown optimizer action")


def operate(workspace, state_path, action, packet, apply=False):
    root = plain(workspace).resolve()
    state_path = contained(root, state_path)
    if not isinstance(packet, dict):
        raise ValueError("Packet must be an object")
    def run():
        original = read(state_path) if state_path.exists() else None
        if action == "init":
            if original is not None:
                raise ValueError("Existing optimizer state is preserved")
            updated = initialize(root, state_path, packet)
            status = "initialized"
        else:
            if original is None:
                raise ValueError("Initialize independent controls first")
            updated = json.loads(json.dumps(original))
            status = transition(root, state_path, updated, action, packet)
        changed = updated != original
        if apply and changed:
            write_atomic(state_path, updated)
        return {"status": status, "applied": bool(apply and changed), "deployed": False,
                "state": updated,
                "evidence_limit": "Local declarations and artifact hashes, not authenticated execution or scientific proof"}
    if not apply:
        return run()
    if not state_path.parent.is_dir():
        raise ValueError("Create the designated record directory before applying")
    with lock(state_path):
        return run()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["init", "status", "event", "candidate", "freeze", "settle",
                                         "revise", "validate", "publish"])
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--packet", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        result = operate(args.workspace, args.state, args.action,
                         read(args.packet) if args.packet else {}, args.apply)
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "blocked", "type": type(exc).__name__,
                          "detail": str(exc) if isinstance(exc, ValueError) else "Invalid or unavailable record",
                          "deployed": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

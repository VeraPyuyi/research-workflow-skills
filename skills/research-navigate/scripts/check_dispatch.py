"""Offline admission check for one direct task. Does not call models or reserve quota."""

import argparse
from collections import Counter
import json
from pathlib import Path, PurePosixPath, PureWindowsPath


import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from math_work import validate_math_work
from model_identity import model_family, NATIVE_MODELS, LEGACY_NATIVE_MODELS

REGISTRY = Path(__file__).resolve().parents[1] / "references/model-routing.json"

def review_errors(plan):
    """Validate declared inputs; this cannot inspect content or enforce isolation."""
    errors = []
    mode = plan.get("review_mode", "internal")
    if mode not in ("internal", "venue_blind"):
        return ["Unknown review mode"]
    if mode != "venue_blind":
        return errors
    if plan.get("stage") != "research-review":
        errors.append("Venue review belongs to research-review")
    if plan.get("fork_context") is not False or plan.get("new_agent") is not True:
        errors.append("Venue review requires a new agent with fork_context false")
    number = plan.get("review_round")
    if type(number) is not int or number not in (1, 2):
        errors.append("The default venue review contract has rounds 1 and 2")
    for field in ("manuscript_revision", "venue_profile"):
        if not isinstance(plan.get(field), str) or not plan[field].strip():
            errors.append(f"Missing {field}")
    inputs = plan.get("allowed_inputs")
    if not isinstance(inputs, list) or not inputs:
        return errors + ["Venue review needs an explicit input manifest"]
    seen = set()
    for item in inputs:
        if not isinstance(item, dict):
            errors.append("Invalid venue review input")
            continue
        kind = item.get("kind")
        if kind not in ("manuscript", "submitted_attachment", "venue_criteria"):
            errors.append("Internal history, previous reviews and other inputs are not allowed")
            continue
        seen.add(kind)
        if any(not isinstance(item.get(key), str) or not item[key].strip()
               for key in ("ref", "revision")):
            errors.append("Review inputs require artifact references and revisions")
        if kind == "manuscript" and item.get("revision") != plan.get("manuscript_revision"):
            errors.append("Review manuscript revision does not match the frozen submission")
        if kind == "venue_criteria" and item.get("revision") != plan.get("venue_profile"):
            errors.append("Venue criteria do not match the declared profile")
    if not {"manuscript", "venue_criteria"}.issubset(seen):
        errors.append("Both manuscript and venue criteria are required")
    return errors


def identity(model, models=None):
    """Conservatively treat known same-model free channels as one author identity."""
    registered = (models or {}).get(model, {})
    return model_family(model, registered.get("model_family"))


def overlap(first, second):
    # The invoking coordinator must supply resolved absolute paths (no aliases).
    def absolute(value):
        if not isinstance(value, str):
            raise ValueError("Write paths must be strings")
        cls = PurePosixPath if value.startswith("/") and not value.startswith("//") else PureWindowsPath
        return cls(value)

    a, b = absolute(first), absolute(second)
    if not a.is_absolute() or not b.is_absolute() or ".." in a.parts or ".." in b.parts:
        raise ValueError("Write paths must be resolved absolute paths")
    return a == b or a in b.parents or b in a.parents


def check(plan, registry=None):
    registry = registry or json.loads(REGISTRY.read_text(encoding="utf-8"))
    models = {item["id"]: item for item in registry["models"]}
    errors = review_errors(plan) + validate_math_work(plan)
    model = plan.get("model", "")
    selected = models.get(model)
    if isinstance(model, str) and model.startswith("google-vertex/"):
        # No verified credit-backed adapter is implemented in this release.
        # Caller flags cannot turn billing/quota evidence into promotional credit.
        errors.append(
            "Vertex is on hold: Trial credit for GenAI App Builder coverage and "
            "no-paid-overage enforcement are unverified; generic allowance "
            "confirmation cannot authorize dispatch"
        )
    if selected and selected.get("dispatch_block_reason"):
        errors.append("Endpoint needs re-verification: " + selected["dispatch_block_reason"])
    if (plan.get("requires_hard_output_cap") is True
            and (not selected or selected.get("hard_output_cap_verified") is not True)):
        errors.append("A requested output limit is not a verified upstream hard cap")
    active = plan.get("active", [])
    if not isinstance(active, list):
        active = []
        errors.append("Active task inventory must be a list")
    if not selected:
        errors.append("Use a registered fully qualified direct endpoint, not a group")
    if plan.get("stage") not in registry["stages"]:
        errors.append("Unknown research stage")
    if not plan.get("id"):
        errors.append("Missing task identity")
    if plan.get("budget_state") != "within":
        errors.append("Budget or commitments are not reconciled within the allowance")
    if not plan.get("capability_record"):
        errors.append("Missing current access/context/tools/channel-policy evidence")
    if plan.get("data_allowed") is not True:
        errors.append("Data permission has not been established")
    if plan.get("provider_fallback") != []:
        errors.append("Strict dispatch requires an explicitly empty provider fallback")
    call_type = plan.get("call_type", "generative")
    kind = selected.get("kind", "generative") if selected else None
    if call_type != kind:
        errors.append("The task must use the endpoint's declared service type")
    if kind == "structured_decision":
        if selected.get("capability_status") != "native_schema_verified":
            errors.append("This separate decision channel has no verified adapter")
        if plan.get("effort") is not None:
            errors.append("Structured decisions do not accept a reasoning effort")
        if not selected.get("adapter") or plan.get("adapter") != selected["adapter"]:
            errors.append("Use the native decision adapter, bypassing mixed groups")
        types = plan.get("decision_types")
        if (not isinstance(types, list) or not types
                or any(item not in ("Choice", "Score", "Noul") for item in types)):
            errors.append("Native decisions require supported primitive types")
        if plan.get("contains_images") is not False:
            errors.append("Native decision packets use inspected text, not image payloads")
        if plan.get("review_mode") == "venue_blind":
            errors.append("A decision service cannot perform a venue review")
    else:
        efforts = plan.get("supported_efforts")
        if not isinstance(efforts, list) or plan.get("effort") not in efforts:
            errors.append("Requested effort is not verified; do not rely on rounding")
        if (selected and selected.get("effort_mode") == "fixed"
                and plan.get("effort") != selected.get("fixed_effort")):
            errors.append("This endpoint has a fixed effort; no synthetic override")
        tiers = selected.get("allowed_service_tiers") if selected else None
        if tiers is not None and plan.get("service_tier", "default") not in tiers:
            errors.append("Requested service tier is outside the recorded account coverage")
    if type(plan.get("contains_images")) is not bool:
        errors.append("Inspect image presence across the complete request history")
    elif plan["contains_images"] and plan.get("direct_vision") is not True:
        errors.append("Image input could trigger an auxiliary vision-model call")
    if type(plan.get("free_only")) is not bool:
        errors.append("Specify free-only or authorized-budget dispatch")
    if plan.get("contains_images") is True and plan.get("direct_vision") is True:
        if plan.get("vision_endpoint_verified") is not True:
            errors.append("Direct vision endpoint and auxiliary-call behavior are unverified")
    if plan.get("tools_allowed", True) is not True:
        errors.append("Required tools are not permitted for this task")
    if selected:
        if plan.get("free_only") and not selected["free"]:
            errors.append("Billed endpoint cannot satisfy a free-only task")
        if not selected["free"] and not plan.get("cost_authorization"):
            errors.append("Missing applicable cost authorization reference")
        if not selected["free"] and (
            plan.get("allowance_coverage") != "confirmed" or not plan.get("allowance_record")
        ):
            errors.append("Account allowance coverage is unknown or unreferenced")
        author = plan.get("author_model")
        author_evidence = plan.get("author_evidence")
        review_requires_provenance = (
            (plan.get("stage") == "research-review" and kind == "generative")
            or author is not None
        )
        if review_requires_provenance and not author:
            errors.append("Independent review needs the author's model identity")
        if author and (author not in models or not author_evidence or
                       identity(author, models) == identity(model, models)):
            errors.append("Independent review needs a known different model")

    pools = Counter()
    ids = set()
    writes = plan.get("write_paths", [])
    if not isinstance(writes, list):
        writes = []
        errors.append("Write scope must be a list")
    try:
        for path in writes:
            overlap(path, path)
    except (ValueError, TypeError):
        errors.append("Write scope contains an unresolved or invalid path")
        writes = []
    for task in active:
        if not isinstance(task, dict):
            errors.append("Invalid active task record")
            continue
        if task.get("status") not in ("running", "reserved"):
            errors.append("Reconcile unknown or stale active task state before expansion")
        task_id = task.get("id")
        if not task_id or task_id in ids or task_id == plan.get("id"):
            errors.append("Duplicate or missing task identity; do not resubmit")
        ids.add(task_id)
        prior = models.get(task.get("model"))
        if prior:
            pools[prior["quota_pool"]] += 1
        else:
            errors.append("Active task has an unknown quota pool")
        try:
            if any(overlap(a, b) for a in writes for b in task.get("write_paths", [])):
                errors.append("Concurrent write scopes overlap")
        except (ValueError, TypeError):
            errors.append("Active write scope is unresolved")
    policy = registry["policy"]
    if len(active) >= policy["max_active_workers"]:
        errors.append("Global worker capacity reached")
    if selected:
        pool = selected["quota_pool"]
        confirmed = plan.get("confirmed_pools", [])
        limit = (policy["max_concurrency_per_confirmed_pool"] if pool in confirmed
                 else policy["max_concurrency_unknown_pool"])
        if pools[pool] >= limit:
            errors.append("Shared quota pool capacity reached")
    return {
        "status": "blocked" if errors else "ready-for-dispatch",
        "model": model if selected else None,
        "effort": plan.get("effort"),
        "call_type": call_type,
        "errors": errors,
        "executed": False,
        "reserved": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path, help="JSON projection of current task records")
    args = parser.parse_args()
    try:
        packet = json.loads(args.packet.read_text(encoding="utf-8-sig"))
        if not isinstance(packet, dict):
            raise ValueError("Expected an object")
        result = check(packet)
    except (OSError, ValueError, TypeError, KeyError):
        print(json.dumps({"status": "blocked", "errors": ["Invalid or unreadable packet"],
                          "executed": False, "reserved": False}))
        return 1
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "ready-for-dispatch" else 1


if __name__ == "__main__":
    raise SystemExit(main())

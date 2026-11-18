"""Optional math handoff validation and pure return consumption.

The coordinator persists under its existing state lock and starts the returned
action. This module neither schedules work nor certifies mathematical truth.
"""
import copy
import hashlib
import json


def text(value):
    return isinstance(value, str) and bool(value.strip())


def validate_math_work(plan):
    if "math_work" not in plan:
        return []
    work = plan["math_work"]
    if not isinstance(work, dict):
        return ["math_work must be an object"]
    errors = []
    for name in ("original_spec_ref", "original_spec_revision", "active_obligation",
                 "parent_obligation", "parent_task_id", "return_to",
                 "continuation_owner", "next_discriminating_action", "obstacle_id"):
        if not text(work.get(name)):
            errors.append("math_work requires one nonempty " + name)
    if work.get("parent_task_id") == plan.get("id"):
        errors.append("math_work child cannot be its own parent")
    for name in ("theorem_uses", "established_connection", "remaining_connection"):
        value = work.get(name)
        if not isinstance(value, list) or any(not text(item) for item in value):
            errors.append("math_work " + name + " must be a list of references or statements")
    parent = plan.get("parent_binding")
    if parent is not None:
        if not isinstance(parent, dict):
            errors.append("math_work parent_binding must be an object")
        else:
            for name in ("parent_task_id", "parent_obligation", "original_spec_ref", "original_spec_revision",
                         "return_to", "continuation_owner"):
                if parent.get(name) != work.get(name):
                    errors.append("math_work differs from parent_binding: " + name)
    return errors


def consume_return(state, event, actor):
    """Idempotent state transform; external single-writer lock remains required."""
    if not isinstance(state, dict) or not isinstance(event, dict):
        raise ValueError("Return and parent state must be objects")
    work = state.get("math_work", {})
    errors = validate_math_work({"id": event.get("child_task_id"), "math_work": work})
    if errors:
        raise ValueError("; ".join(errors))
    if actor != work["continuation_owner"]:
        raise ValueError("Only the continuation owner may consume a child return")
    if event.get("parent_task_id") != state.get("id"):
        raise ValueError("Return belongs to a different parent task")
    for name in ("parent_task_id", "parent_obligation", "original_spec_ref",
                 "original_spec_revision", "return_to"):
        if event.get(name) != work.get(name):
            raise ValueError("Stale or mismatched return: " + name)
    delegations = state.get("delegations")
    binding = (delegations.get(event.get("child_task_id"))
               if isinstance(delegations, dict) and text(event.get("child_task_id")) else None)
    if not isinstance(binding, dict):
        raise ValueError("Return child has no recorded delegation")
    for name in ("original_spec_ref", "original_spec_revision", "active_obligation",
                 "parent_task_id", "parent_obligation", "return_to"):
        if not text(binding.get(name)) or event.get(name) != binding[name]:
            raise ValueError("Return differs from recorded child delegation: " + name)
    if binding.get("continuation_owner") != actor:
        raise ValueError("Return delegation has a different continuation owner")
    for name in ("id", "child_task_id", "connection_review_ref", "next_action"):
        if not text(event.get(name)):
            raise ValueError("Return requires " + name)
    for name in ("artifact_refs", "supersedes_pending"):
        if (not isinstance(event.get(name), list)
                or any(not text(item) for item in event[name])):
            raise ValueError("Return requires a list: " + name)
    if not event["artifact_refs"]:
        raise ValueError("Return must reference the actual result")
    digest = hashlib.sha256(json.dumps(event, sort_keys=True).encode()).hexdigest()
    changed = copy.deepcopy(state)
    consumed = changed.setdefault("consumed_returns", {})
    if event["id"] in consumed:
        if consumed[event["id"]]["digest"] != digest:
            raise ValueError("Conflicting content for an already consumed return")
        return changed, {"status": "already-consumed", "next_action": None, "executed": False}
    consumed[event["id"]] = {"digest": digest, "artifact_refs": event["artifact_refs"],
                            "connection_review_ref": event["connection_review_ref"],
                            "owner": actor, "next_action": event["next_action"]}
    for task in changed.get("tasks", []):
        if task.get("id") in event["supersedes_pending"] and task.get("status") == "pending":
            task.update(status="superseded", superseded_by=event["id"])
    changed["next_action"] = event["next_action"]
    return changed, {"status": "consumed", "next_action": event["next_action"],
                     "executed": False, "proof_verified": False}

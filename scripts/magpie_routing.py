"""Offline Magpie smart-split preparation and bounded apply helper."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROUTING = ROOT / "skills" / "research-navigate" / "references" / "model-routing.json"
DEFAULT_ARTIFACT_DIR = ROOT / ".build" / "model-collaboration" / "magpie"
DEFAULT_CONFIG = Path.home() / ".config" / "magpie" / "providers.json"
DEFAULT_CATALOG = Path.home() / ".codex" / "models_cache.json"
GROUP_ID = "smart-split"
KNOWN_GROUP_FIELDS = {
    "id",
    "name",
    "members",
    "routing",
    "rules",
    "classifier",
    "affinity",
    "patience",
    "firstToken",
    "pick",
    "off",
    "levels",
    "effort",
    "context",
    "fast",
    "weights",
    "family",
    "unlists",
    "hidden",
    "disabled",
}
KNOWN_RULE_FIELDS = {
    "use",
    "useEffort",
    "tokens",
    "images",
    "effort",
    "agents",
    "intent",
    "compact",
    "time",
    "folders",
    "exceptFolders",
    "pause",
}
KNOWN_EFFORTS = {"low", "medium", "high", "xhigh", "max", "on"}
MAX_INTENT_CHARS = 200
CLASSIFIER = "typesafe/jev-latest"
INTENTS = {
    "classify": "Structured research task classification and stage routing: identify navigation, retrieval, reuse review, independent review, math, engineering, experiment, analysis, writing, or submission.",
    "optimize": "Workflow retrospective: preserve strengths, identify evidence-backed weaknesses, prepare bounded improvement candidates for milestone validation without changing goals, criteria or budgets.",
    "focus": "Research focus and cumulative topic drift: compare original user theme, current thesis and pivot history; map auxiliary theories or code to core claims and preserve valuable in-theme inquiry.",
    "retrieve": "Literature retrieval: search papers or public sources, verify facts, locate primary evidence, and organize references; deliver sources, not a conclusion.",
    "reuse": "Literature synthesis, reuse review, and contribution assessment: compare prior work and identify reusable versus replacement-needed material.",
    "review": "Independent scientific or mathematical review: check derivations, statistics, interpretations, and conclusion chains for errors and incomparable claims.",
    "math": "Mathematical checking and standard problem solving: verify derivations or calculations, find counterexamples, or solve well-specified problems.",
    "engineering": "Research engineering: implement or repair data cleaning, statistics, numerics, simulation, tests, packaging, or visualization from an approved method.",
    "vision": "Public figure, equation, or screenshot extraction: extract text, structure, values, or comparisons without extending the research conclusion.",
    "consistency": "Long-evidence consistency review: check supplied reports or appendices for definition, symbol, record, figure, and conclusion consistency.",
    "hard": "Difficult research: original directions, nonstandard proofs, unresolved mechanisms, experiment design, or causal structure, including dependent research coding.",
    "formal": "Formal derivation and standard implementation: turn an approved method into verifiable mathematics, code, tests, or reproduction steps.",
    "experiment": "Experiment and protocol coordination: turn an approved protocol into executable steps, checks, records, and resource limits without changing the method.",
    "writing": "Routine research writing: draft or revise short sections, summaries, translations, or polished prose from supplied evidence and an approved claim.",
    "manuscript": "Final manuscript integration: assemble approved chapters, figures, definitions, and citations into a consistent submission-ready manuscript.",
    "routine": "Routine research assistance: explain established concepts, answer basic questions, summarize one short item, or calculate from a known formula.",
}
@dataclass(frozen=True)
class MemberSpec:
    member: str
    provider: str
    model: str
    effort: str | None = None


@dataclass(frozen=True)
class Plan:
    before_group: dict[str, Any]
    after_group: dict[str, Any]
    before_sanitized: dict[str, Any]
    after_sanitized: dict[str, Any]
    evidence: dict[str, Any]
    diff_text: str
    before_hash: str
    after_hash: str
    config_hash_before: str


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_config_bytes(path: Path) -> bytes:
    """Read config bytes once so the plan hash matches the parsed payload."""
    return path.read_bytes()


def _read_back_config_bytes(path: Path) -> bytes:
    return path.read_bytes()


def _before_atomic_replace(path: Path) -> None:
    """Hook for tests to simulate a concurrent writer after backup."""
    return None


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _is_reparse_point(path: Path) -> bool:
    if path.is_symlink() or getattr(path, "is_junction", lambda: False)():
        return True
    try:
        attributes = path.lstat().st_file_attributes
    except (AttributeError, OSError):
        return False
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def resolve_config_path(path: Path) -> Path:
    requested = path.expanduser().absolute()
    for ancestor in (requested, *requested.parents):
        if _is_reparse_point(ancestor):
            raise ValueError(f"config path or ancestor must not be a reparse point: {ancestor}")
    return requested.resolve(strict=False)


def assert_config_target(path: Path, requested: Path) -> None:
    resolved = resolve_config_path(path)
    requested = resolve_config_path(requested)
    if resolved != requested:
        raise ValueError(f"resolved config path {resolved} does not match requested {requested}")


def project_group(group: dict[str, Any]) -> dict[str, Any]:
    """Project only known routing fields; never copy provider configuration."""
    allowed = {
        "id",
        "name",
        "members",
        "routing",
        "affinity",
        "patience",
        "firstToken",
        "pick",
        "off",
        "levels",
        "effort",
        "context",
        "fast",
        "weights",
        "family",
        "unlists",
        "hidden",
        "disabled",
        "rules",
        "classifier",
    }
    projected = {
        key: json.loads(json.dumps(group[key]))
        for key in allowed
        if key in group and key not in {"rules"}
    }
    if "rules" in group:
        projected["rules"] = [
            {key: json.loads(json.dumps(value)) for key, value in rule.items()
             if key in KNOWN_RULE_FIELDS}
            for rule in group["rules"]
        ]
    return projected


def sanitize_config(config: dict[str, Any]) -> dict[str, Any]:
    """Allowlist projection for offline evidence; never serializes credentials."""
    providers = []
    for provider in config.get("providers", []):
        providers.append(
            {
                "id": provider.get("id"),
                "models": list(provider.get("models") or []),
                "fallback_present": bool(provider.get("fallback")),
            }
        )
    return {
        "providers": providers,
        "groups": [project_group(group) for group in config.get("groups", [])],
    }


def split_member(member: str) -> MemberSpec:
    if member.startswith("group/"):
        return MemberSpec(member=member, provider="group", model=member.split("/", 1)[1], effort=None)
    if "/" not in member:
        raise ValueError(f"member {member!r} must be provider/model or group/id")
    provider, rest = member.split("/", 1)
    model, effort = rest, None
    if ":" in rest:
        model, effort = rest.rsplit(":", 1)
        if effort not in KNOWN_EFFORTS:
            model, effort = rest, None
    return MemberSpec(member=member, provider=provider, model=model, effort=effort)


def member_model(member: str) -> str:
    """Return provider/model without a verified effort suffix."""
    spec = split_member(member)
    return f"{spec.provider}/{spec.model}"


def provider_models(config: dict[str, Any]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for provider in config.get("providers", []):
        pid = provider.get("id")
        if not pid:
            continue
        models = set(provider.get("models") or [])
        models.update(provider.get("unlisted") or [])
        out[pid] = {str(m) for m in models}
    return out


def load_effort_evidence(catalog_path: Path, providers: set[str] | None = None) -> dict[str, Any]:
    """Read only capability metadata from the local Codex catalog."""
    evidence: dict[str, Any] = {"source": str(catalog_path), "levels": {}}
    if not catalog_path.exists():
        return evidence
    catalog = load_json(catalog_path)
    for model in catalog.get("models", []):
        slug = model.get("slug")
        raw_levels = model.get("supported_reasoning_levels")
        if not slug or not isinstance(raw_levels, list):
            continue
        levels = []
        for level in raw_levels:
            effort = level.get("effort") if isinstance(level, dict) else level
            if isinstance(effort, str) and effort:
                levels.append(effort)
        if not levels:
            continue
        if "/" in slug:
            evidence["levels"][slug] = levels
            continue
        evidence["levels"][f"codex/{slug}"] = levels
    return evidence


def supported_efforts(member: str, evidence: dict[str, Any]) -> list[str]:
    spec = split_member(member)
    if spec.provider == "group":
        return []
    levels = evidence.get("levels", {})
    return list(levels.get(f"{spec.provider}/{spec.model}", []))


def validate_group_fields(group: dict[str, Any]) -> None:
    unknown = sorted(set(group) - KNOWN_GROUP_FIELDS)
    if unknown:
        raise ValueError(f"unsupported group fields: {', '.join(unknown)}")
    for rule in group.get("rules", []):
        unknown_rule = sorted(set(rule) - KNOWN_RULE_FIELDS)
        if unknown_rule:
            raise ValueError(f"unsupported rule fields: {', '.join(unknown_rule)}")
        intent = rule.get("intent", "")
        if isinstance(intent, str) and len(intent) > MAX_INTENT_CHARS:
            raise ValueError(f"intent exceeds {MAX_INTENT_CHARS} characters")
        if rule.get("use") not in group.get("members", []):
            raise ValueError(f"rule target {rule.get('use')} is not a group member")


def validate_members(group: dict[str, Any], catalog: dict[str, set[str]], evidence: dict[str, Any]) -> None:
    for member in group.get("members", []):
        spec = split_member(member)
        if spec.provider == "group":
            continue
        if spec.model not in catalog.get(spec.provider, set()):
            raise ValueError(f"member {member} is not in provider catalog")
        if spec.effort:
            allowed = supported_efforts(member, evidence)
            if not allowed:
                raise ValueError(f"no supported effort evidence for {member}")
            if spec.effort not in allowed:
                raise ValueError(f"unsupported effort {spec.effort} for {member}; allowed={allowed}")
    for rule in group.get("rules", []):
        use = rule.get("use")
        if use not in group.get("members", []):
            raise ValueError(f"rule target {use} is not a group member")
        use_effort = rule.get("useEffort")
        if use_effort:
            if use_effort not in KNOWN_EFFORTS:
                raise ValueError(f"unsupported useEffort {use_effort}")
            allowed = supported_efforts(use, evidence)
            if not allowed:
                raise ValueError(f"no supported effort evidence for rule target {use}")
            if use_effort not in allowed:
                raise ValueError(f"unsupported useEffort {use_effort} for {use}")


def build_target_group(routing_path: Path, evidence: dict[str, Any]) -> dict[str, Any]:
    routing = load_json(routing_path)
    free_ids = [item["id"] for item in routing["models"]
                if item.get("free") and item.get("kind", "generative") == "generative"
                and not item["id"].startswith("google-vertex/")
                and item.get("group_eligible", True) and not item.get("dispatch_block_reason")]
    effort_by_id = {item["id"]: item.get("effort") for item in routing["models"]}
    def verified(member: str, wanted: str) -> str:
        levels = supported_efforts(member, evidence)
        return f"{member}:{wanted}" if wanted in levels else member

    members = [
        verified("codex/gpt-6-astra", "max"),
        verified("codex/gpt-6.1-sol", "max"),
    ]
    for model_id in free_ids:
        effort = effort_by_id.get(model_id, "")
        members.append(verified(model_id, effort) if effort else model_id)
    account_rules = []
    for item in routing["models"]:
        # No Vertex route has verified App Builder credit/no-overage coverage.
        # Generic group eligibility must not override this billing hold.
        if item["id"].startswith("google-vertex/"):
            continue
        intents = item.get("automatic_group_intents", [])
        if (not intents or item.get("group_eligible") is not True
                or item.get("kind", "generative") != "generative"
                or item.get("dispatch_block_reason")):
            continue
        effort = (item.get("fixed_effort") if item.get("effort_mode") == "fixed"
                  else item.get("effort"))
        # Never turn a fixed subscription effort into an inherited group effort.
        if not effort or effort not in supported_efforts(item["id"], evidence):
            continue
        member = f"{item['id']}:{effort}"
        if member not in members:
            members.append(member)
        if not isinstance(intents, list) or any(
            not isinstance(intent, str) or not intent.strip()
            or len(intent) > MAX_INTENT_CHARS for intent in intents
        ):
            raise ValueError(f"invalid automatic group intents for {item['id']}")
        account_rules.extend({"use": member, "intent": intent} for intent in intents)
    def exact_member(model_id: str) -> str:
        return next(member for member in members if member_model(member) == model_id)

    rules = account_rules + [
        {"use": exact_member("opencode-zen/nemotron-3.5-lightning-free"), "intent": INTENTS["classify"]},
        {"use": exact_member("workbuddy-ai/step-5-preview"), "intent": INTENTS["optimize"]},
        {"use": exact_member("workbuddy-ai/step-5-preview"), "intent": INTENTS["focus"]},
        {"use": exact_member("workbuddy-ai/hy3"), "intent": INTENTS["retrieve"]},
        {"use": exact_member("workbuddy-ai/step-5-preview"), "intent": INTENTS["reuse"]},
        {"use": exact_member("workbuddy-ai/deepseek-v4.1-flash"), "intent": INTENTS["review"]},
        {"use": exact_member("opencode-zen/beam-free"), "intent": INTENTS["math"]},
        {"use": exact_member("opencode-zen/glm-5.3-flash-free"), "intent": INTENTS["engineering"]},
        {"use": exact_member("opencode-zen/nemotron-3.5-super-vl-free"), "intent": INTENTS["vision"]},
        {"use": exact_member("workbuddy-ai/step-5-preview"), "intent": INTENTS["consistency"]},
        {"use": exact_member("codex/gpt-6-astra"), "intent": INTENTS["hard"]},
        {"use": exact_member("codex/gpt-6.1-sol"), "intent": INTENTS["formal"]},
        {"use": exact_member("codex/gpt-6.1-sol"), "intent": INTENTS["experiment"]},
        {"use": exact_member("workbuddy-ai/step-5-preview"), "intent": INTENTS["writing"]},
        {"use": exact_member("codex/gpt-6-astra"), "intent": INTENTS["manuscript"]},
        {"use": exact_member("workbuddy-ai/step-5-preview"), "intent": INTENTS["routine"]},
    ]
    for rule in rules:
        if len(rule["intent"]) > MAX_INTENT_CHARS:
            raise ValueError(f"intent exceeds {MAX_INTENT_CHARS} characters")
    return {
        "id": GROUP_ID,
        "name": "科研",
        "members": members,
        "routing": "order",
        "affinity": "turn",
        "patience": -1,
        "rules": rules,
        "classifier": CLASSIFIER,
    }


def replace_group(config: dict[str, Any], new_group: dict[str, Any]) -> dict[str, Any]:
    updated = json.loads(json.dumps(config))
    groups = updated.setdefault("groups", [])
    for index, group in enumerate(groups):
        if group.get("id") == GROUP_ID:
            groups[index] = new_group
            return updated
    raise ValueError(f"group {GROUP_ID} not found")


def extract_group(config: dict[str, Any]) -> dict[str, Any]:
    for group in config.get("groups", []):
        if group.get("id") == GROUP_ID:
            return group
    raise ValueError(f"group {GROUP_ID} not found")


def diff_groups(before: dict[str, Any], after: dict[str, Any]) -> str:
    before_lines = json.dumps(before, indent=2, ensure_ascii=False).splitlines(keepends=True)
    after_lines = json.dumps(after, indent=2, ensure_ascii=False).splitlines(keepends=True)
    return "".join(difflib.unified_diff(before_lines, after_lines, fromfile="smart-split.before.json", tofile="smart-split.after.json"))


def build_plan(config_path: Path, routing_path: Path, artifact_dir: Path, catalog_path: Path = DEFAULT_CATALOG) -> Plan:
    config_path = resolve_config_path(config_path)
    raw = read_config_bytes(config_path)
    config = json.loads(raw.decode("utf-8"))
    before_group = extract_group(config)
    validate_group_fields(before_group)
    before_export = project_group(before_group)
    evidence = load_effort_evidence(catalog_path, set(provider_models(config)))
    after_group = build_target_group(routing_path, evidence)
    validate_group_fields(after_group)
    validate_members(after_group, provider_models(config), evidence)
    updated = replace_group(config, after_group)
    before_sanitized = sanitize_config(config)
    after_sanitized = sanitize_config(updated)
    diff_text = diff_groups(before_export, after_group)
    before_hash = sha256_bytes(json.dumps(before_group, sort_keys=True, ensure_ascii=False).encode("utf-8"))
    after_hash = sha256_bytes(json.dumps(after_group, sort_keys=True, ensure_ascii=False).encode("utf-8"))
    config_hash_before = sha256_bytes(raw)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    dump_json(artifact_dir / "smart-split.before.sanitized.json", before_sanitized)
    dump_json(artifact_dir / "smart-split.after.sanitized.json", after_sanitized)
    dump_json(artifact_dir / "smart-split.before.group.json", before_export)
    dump_json(artifact_dir / "smart-split.after.group.json", after_group)
    dump_json(artifact_dir / "effort-evidence.json", evidence)
    (artifact_dir / "smart-split.diff").write_text(diff_text, encoding="utf-8")
    dump_json(
        artifact_dir / "manifest.json",
        {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "group_id": GROUP_ID,
            "before_group_sha256": before_hash,
            "after_group_sha256": after_hash,
            "config_sha256_before": config_hash_before,
            "notes": [
                "Group rules prioritize members; they do not pin execution.",
                "Strict free tasks must bypass group/smart-split via direct exact endpoints.",
            ],
        },
    )
    return Plan(
        before_group=before_group,
        after_group=after_group,
        before_sanitized=before_sanitized,
        after_sanitized=after_sanitized,
        evidence=evidence,
        diff_text=diff_text,
        before_hash=before_hash,
        after_hash=after_hash,
        config_hash_before=config_hash_before,
    )


def backup_config(config_path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup = config_path.with_name(f"{config_path.name}.bak.{stamp}-{uuid.uuid4().hex}")
    if backup.exists() or _is_reparse_point(backup):
        raise ValueError(f"backup path is not a fresh regular file: {backup}")
    shutil.copy2(config_path, backup)
    os.chmod(backup, stat.S_IRUSR | stat.S_IWUSR)
    return backup


def atomic_write_config(config_path: Path, payload: str) -> Path:
    temp = config_path.with_name(f"{config_path.name}.{uuid.uuid4().hex}.tmp")
    if temp.exists() or _is_reparse_point(temp):
        raise ValueError(f"temporary path is not a fresh regular file: {temp}")
    temp.write_text(payload, encoding="utf-8")
    written = temp.read_bytes()
    expected = payload.encode("utf-8")
    if written.replace(b"\r\n", b"\n") != expected:
        raise ValueError("temporary payload hash mismatch")
    if written != expected:
        temp.write_bytes(expected)
    os.replace(temp, config_path)
    return temp


def apply_plan(config_path: Path, plan: Plan, expected_before_hash: str | None) -> dict[str, Any]:
    config_path = resolve_config_path(config_path)
    assert_config_target(config_path, config_path)
    raw = read_config_bytes(config_path)
    current_hash = sha256_bytes(raw)
    if current_hash != plan.config_hash_before:
        raise ValueError("config changed since plan generation; aborting apply")
    if expected_before_hash and current_hash != expected_before_hash:
        raise ValueError("config changed since plan generation; aborting apply")
    config = json.loads(raw.decode("utf-8"))
    updated = replace_group(config, plan.after_group)
    validate_group_fields(plan.after_group)
    validate_members(plan.after_group, provider_models(config), plan.evidence)
    payload = json.dumps(updated, indent=2, ensure_ascii=False) + "\n"
    prepared_hash = sha256_bytes(payload.encode("utf-8"))
    backup = backup_config(config_path)
    _before_atomic_replace(config_path)
    if sha256_bytes(read_config_bytes(config_path)) != current_hash:
        raise ValueError("config changed since plan generation; aborting apply")
    atomic_write_config(config_path, payload)
    try:
        written = _read_back_config_bytes(config_path)
    except OSError as exc:
        raise ValueError(f"read-back failed: {exc}") from exc
    if sha256_bytes(written) != prepared_hash:
        raise ValueError("read-back mismatch")
    written_config = json.loads(written.decode("utf-8"))
    if extract_group(written_config) != plan.after_group:
        raise ValueError("read-back mismatch")
    protected_before = json.loads(raw.decode("utf-8"))
    protected_before["groups"] = [group for group in protected_before.get("groups", []) if group.get("id") != GROUP_ID]
    protected_after = json.loads(json.dumps(written_config))
    protected_after["groups"] = [group for group in protected_after.get("groups", []) if group.get("id") != GROUP_ID]
    if protected_before != protected_after:
        raise ValueError("read-back mismatch")
    return {
        "backup": str(backup),
        "config_sha256_after": sha256_bytes(written),
        "group_sha256_after": plan.after_hash,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--routing", type=Path, default=DEFAULT_ROUTING)
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--apply", action="store_true", help="apply the prepared smart-split update")
    parser.add_argument("--expected-before-hash", help="abort apply when live config hash differs")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config_path = resolve_config_path(args.config)
    assert_config_target(config_path, args.config)
    plan = build_plan(config_path, args.routing, args.artifact_dir, args.catalog)
    print(json.dumps({"mode": "apply" if args.apply else "dry-run", "artifact_dir": str(args.artifact_dir), "before_hash": plan.before_hash, "after_hash": plan.after_hash, "config_hash_before": plan.config_hash_before}, indent=2))
    if args.apply:
        result = apply_plan(config_path, plan, args.expected_before_hash or plan.config_hash_before)
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

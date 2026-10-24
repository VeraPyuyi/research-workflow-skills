"""Build portable workflow candidates and inspect/adopt project records (stdlib only)."""

import argparse
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile


SCHEMA_VERSION = 1
RELEASE_PATH = "research-navigate/references/workflow-release.json"
ROUTING_PATH = "research-navigate/references/model-routing.json"
DESIGNATED_STATES = ("project-state.json", ".research/project.json")
LOCAL_SKILLS = (".agents/skills", ".codex/skills", "skills")
TRUST = "Supplied receipt declarations; no cryptographic external trust or scientific proof."
RUNTIME_PROFILES = ("magpie", "codex-native")
LEGACY_RELEASE_ID = "research-20261024-jev-autonomy-v1"
LEGACY_BUNDLE_DIGEST = "sha256:ae6c9e10217a8dd14b4aab2c736366340ea568f533f47ff59671732c5d121d63"
_VERSION = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:\.(0|[1-9][0-9]*))?\Z")
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
_HASH = re.compile(r"[0-9a-f]{64}\Z")
_RESERVED = re.compile(r"(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?\Z", re.I)


class LockError(ValueError):
    """Another writer owns the record lock, or a stale lock needs inspection."""


def _checked_path(path):
    if ".." in Path(path).parts:
        raise ValueError(f"Parent traversal is unsupported: {path}")
    path = Path(os.path.abspath(os.fspath(path)))
    for ancestor in (*reversed(path.parents), path):
        try:
            info = ancestor.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError(f"Symlink, junction or reparse point is unsupported: {ancestor}")
    return path


def _directory(path):
    path = _checked_path(path)
    if not path.is_dir():
        raise ValueError(f"Directory does not exist: {path}")
    return path


def _relative(root, value):
    value = os.fspath(value)
    parts = value.split("/")
    if (not value or "\\" in value or ":" in value
            or any(part in ("", ".", "..") or part.endswith((".", " "))
                   or _RESERVED.fullmatch(part) or any(ord(c) < 32 for c in part)
                   or any(c in '<>"|?*' for c in part) for part in parts)):
        raise ValueError(f"Expected a portable project-relative path: {value!r}")
    path = _checked_path(root.joinpath(*parts))
    if not path.is_relative_to(root):
        raise ValueError(f"Path escapes its root: {value}")
    return path


def _object_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON field: {key}")
        result[key] = value
    return result


def _invalid_constant(value):
    raise ValueError(f"Non-finite JSON number: {value}")


def _read_json(path):
    path = _checked_path(path)
    if not path.is_file():
        raise ValueError(f"JSON file is missing or not regular: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"),
                      object_pairs_hook=_object_pairs, parse_constant=_invalid_constant)
    if not isinstance(data, dict):
        raise ValueError(f"JSON record must be an object: {path}")
    return data


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def _digest(release):
    return "sha256:" + hashlib.sha256(_canonical({
        key: value for key, value in release.items() if key != "bundle_digest"
    })).hexdigest()


def _version(value):
    match = _VERSION.fullmatch(value) if isinstance(value, str) else None
    if match is None:
        raise ValueError("contract_version must be MAJOR.MINOR or MAJOR.MINOR.PATCH")
    return tuple(int(part or 0) for part in match.groups())


def _profile(value):
    if not isinstance(value, str) or value not in RUNTIME_PROFILES:
        raise ValueError("runtime_profile must be magpie or codex-native")
    return value


def _release_profile(release):
    # Do not insert a field into legacy metadata: that would break its receipt digest.
    if "runtime_profile" in release:
        return _profile(release["runtime_profile"])
    if (release.get("release_id") == LEGACY_RELEASE_ID
            and release.get("bundle_digest") == LEGACY_BUNDLE_DIGEST):
        return "magpie"
    raise ValueError("Unknown unprofiled release; runtime_profile cannot be inferred")


def _references(value, label):
    if not isinstance(value, list) or any(
        not isinstance(ref, str) or not ref.strip() or any(ord(c) < 32 for c in ref)
        for ref in value
    ):
        raise ValueError(f"{label} must be a list of nonempty reference strings")
    return value


def _inventory(root, package_roots=None):
    files = {}

    def visit(path):
        relative = path.relative_to(root).as_posix()
        path = _relative(root, relative)
        if path.name == "__pycache__":
            return
        if path.is_dir():
            for item in sorted(path.iterdir()):
                visit(item)
        elif path.is_file():
            if relative != RELEASE_PATH:
                files[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        else:
            raise ValueError(f"Non-regular or missing packaged resource: {path}")

    paths = (sorted(root.iterdir()) if package_roots is None else
             [_relative(root, name) for name in sorted(package_roots)])
    for path in paths:
        visit(path)
    return files


def _file_hashes(files, root):
    if not isinstance(files, dict) or not files:
        raise ValueError("Release files must be a nonempty hash mapping")
    seen = set()
    for relative, digest in files.items():
        _relative(root, relative)
        if (relative == RELEASE_PATH or "__pycache__" in relative.split("/")
                or not isinstance(digest, str) or not _HASH.fullmatch(digest)):
            raise ValueError(f"Invalid packaged hash: {relative}")
        if relative.casefold() in seen:
            raise ValueError(f"Case-colliding packaged path: {relative}")
        seen.add(relative.casefold())


def _validate_metadata(release, root):
    if type(release.get("schema_version")) is not int or release["schema_version"] != SCHEMA_VERSION:
        raise ValueError("Unsupported release schema_version")
    if not isinstance(release.get("release_id"), str) or not _ID.fullmatch(release["release_id"]):
        raise ValueError("release_id must be a safe nonempty identifier")
    _version(release.get("contract_version"))
    if release.get("status") != "candidate":
        raise ValueError("Packaged metadata must describe a candidate")
    _references(release.get("validation_receipts"), "validation_receipts")
    _file_hashes(release.get("files"), root)
    if release.get("bundle_digest") != _digest(release):
        raise ValueError("Release metadata content digest mismatch")
    _release_profile(release)


def validate_runtime_profile(skills_dir, runtime_profile=None, *, legacy_release=None,
                             manifest_path=None):
    """Check labels against actual model/host routing, including installed suites."""
    root = _directory(skills_dir)
    routing = _read_json(_relative(root, ROUTING_PATH))
    legacy = (isinstance(legacy_release, dict)
              and "runtime_profile" not in legacy_release
              and legacy_release.get("release_id") == LEGACY_RELEASE_ID
              and legacy_release.get("bundle_digest") == LEGACY_BUNDLE_DIGEST
              and _digest(legacy_release) == LEGACY_BUNDLE_DIGEST)
    actual = ("magpie" if "runtime_profile" not in routing and legacy
              else _profile(routing.get("runtime_profile")))
    if runtime_profile is not None and _profile(runtime_profile) != actual:
        raise ValueError("Registry runtime_profile differs from the release or manifest")
    manifest = (_checked_path(manifest_path) if manifest_path is not None else
                _checked_path(root.parent / "skills-manifest.json"))
    if manifest.exists():
        data = _read_json(manifest)
        if "runtime_profile" in data and _profile(data["runtime_profile"]) != actual:
            raise ValueError("Manifest runtime_profile differs from the registry")

    models = routing.get("models")
    if (not isinstance(models, list) or not models
            or any(not isinstance(m, dict) or not isinstance(m.get("id"), str)
                   or m.get("kind") not in ("generative", "structured_decision") for m in models)):
        raise ValueError("Registry runtime_profile requires explicit model identities and kinds")
    ids = [model["id"] for model in models]
    if len(ids) != len(set(ids)):
        raise ValueError("Registry runtime_profile has duplicate model identities")
    generative = {m["id"] for m in models if m["kind"] == "generative"}
    services = {m["id"] for m in models if m["kind"] == "structured_decision"}
    if actual == "magpie":
        if not generative or any("/" not in name for name in ids) or "native_tools" in routing:
            raise ValueError("Magpie runtime_profile requires qualified endpoint routing")
    else:
        native_fields = {"version", "runtime_profile", "captured_at", "policy", "native_tools",
                         "models", "task_roles", "stages", "review_roles", "gates", "decision_services"}
        if set(routing) - native_fields:
            raise ValueError("Native runtime_profile has unsupported routing/configuration fields")
        native_ids = {"gpt-6.1-sol", "gpt-6-astra", "gpt-6-luna"}
        if set(ids) != native_ids or generative != native_ids or len(models) != 3:
            raise ValueError("Native runtime_profile requires exactly Sol, Astra and Luna generative models")
        model_fields = {"id", "model_family", "kind", "quota_pool", "role", "preferred_reasoning_effort",
                        "access", "limitations", "effort", "effort_status"}
        for model in models:
            if (model.get("model_family") != model["id"] or model.get("quota_pool") != "codex"
                    or set(model) - model_fields):
                raise ValueError("Native runtime_profile cannot contain external model routing/configuration")
        native_tools = routing.get("native_tools")
        if (not isinstance(native_tools, dict)
                or set(native_tools) != {"spawn_agent", "wait_agent", "send_input"}
                or any(not isinstance(tool, dict) or tool.get("name") != "multi_agent_v1." + name
                       or set(tool) - {"name", "arguments"} for name, tool in native_tools.items())):
            raise ValueError("Native runtime_profile requires native host tool routing")
        def no_magpie_config(value, field=None):
            if isinstance(value, dict):
                if any("magpie" in key.casefold() for key in value):
                    raise ValueError("Native runtime_profile cannot depend on Magpie configuration")
                for key, child in value.items():
                    no_magpie_config(child, key)
            elif isinstance(value, list):
                for child in value:
                    no_magpie_config(child, field)
            elif (isinstance(value, str) and "magpie" in value.casefold()
                  and field not in {"role", "access", "limitations", "description", "notes"}):
                raise ValueError("Native runtime_profile cannot use Magpie transport/configuration")
        no_magpie_config(routing)
        decision_services = routing.get("decision_services", {})
        if not isinstance(decision_services, dict) or set(decision_services) - {"jev"}:
            raise ValueError("Native decision_services permits only the standalone structured Jev service")
        if "jev" in decision_services:
            service = decision_services["jev"]
            fixed = {
                "kind": "structured_decision", "optional": True,
                "adapter": "scripts/jev_decide.py",
                "explicit_config_fields": ["api_key_env", "models"],
                "endpoint": "https://api.typesafe.ai/v1/systemone",
                "quota_pool": "jev", "max_concurrency": 1,
                "generative_worker": False, "review_eligible": False,
                "primitive_types": ["choice", "score", "noul"],
                "fallback": "native-evidence-comparison",
            }
            fields = set(fixed) | {"default_model", "runtime_models", "credential_env",
                                   "pool_state", "credit_coverage"}
            if (not isinstance(service, dict) or set(service) - fields
                    or any(type(service.get(key)) is not type(value) or service[key] != value
                           for key, value in fixed.items())):
                raise ValueError("Native Jev must remain a standalone optional decision service")
            permitted = service.get("runtime_models")
            if (not isinstance(permitted, list) or not permitted
                    or any(not isinstance(name, str) or len(name) > 128
                           or not re.fullmatch(r"jev-[A-Za-z0-9][A-Za-z0-9._+-]*", name)
                           for name in permitted)
                    or len(set(permitted)) != len(permitted)
                    or service.get("default_model") not in permitted):
                raise ValueError("Native Jev requires an explicit valid runtime model whitelist")
            if (not isinstance(service.get("credential_env"), str)
                    or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", service["credential_env"])):
                raise ValueError("Native Jev credentials must use an environment variable reference")
        services = set(decision_services)

    def model_references(value, allowed):
        if isinstance(value, str):
            if value not in allowed:
                raise ValueError(f"Registry runtime_profile has an unregistered or disallowed route: {value}")
        elif isinstance(value, list):
            for child in value:
                model_references(child, allowed)
        elif isinstance(value, dict):
            for key, child in value.items():
                model_references(child, services if key == "decision_services" else allowed)
        elif type(value) is not bool:
            raise ValueError("Registry runtime_profile has an invalid model route")
    for section in ("stages", "task_roles", "review_roles"):
        if section in routing:
            if not isinstance(routing[section], dict):
                raise ValueError(f"Registry runtime_profile {section} must be an object")
            model_references(routing[section], generative)
    return actual


def _atomic_json(path, value):
    path = _checked_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    _checked_path(path.parent)
    encoded = json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + "\n"
    descriptor, temporary = tempfile.mkstemp(prefix="." + path.name + ".", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        _checked_path(path)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def exclusive_lock(record_path):
    """Fail fast on an exclusive sibling .lock; never steal an existing lock."""
    record_path = _checked_path(record_path)
    lock_path = _checked_path(Path(str(record_path) + ".lock"))
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(lock_path, flags, 0o600)
    except FileExistsError as exc:
        raise LockError(f"Record locked; reconcile owner before retrying: {lock_path}") from exc
    identity = os.fstat(descriptor)
    try:
        with os.fdopen(descriptor, "w", encoding="ascii") as stream:
            stream.write(json.dumps({"pid": os.getpid(), "record": str(record_path)}))
            stream.flush()
            os.fsync(stream.fileno())
        yield
    finally:
        _checked_path(lock_path)
        try:
            current = lock_path.stat()
        except FileNotFoundError:
            current = None
        if current and (current.st_dev, current.st_ino) == (identity.st_dev, identity.st_ino):
            lock_path.unlink()


def build_release(skills_dir, release_id, contract_version, validation_receipts=(), apply=False,
                  runtime_profile=None):
    """Return a deterministic candidate; --apply writes only packaged metadata."""
    root = _directory(skills_dir)
    runtime_profile = _profile(runtime_profile)
    metadata_path = _relative(root, RELEASE_PATH)

    def candidate():
        files = _inventory(root)
        validate_runtime_profile(root, runtime_profile)
        required = ("research-navigate/SKILL.md", "research-navigate/references/workflow-contract.md")
        if any(name not in files for name in required):
            raise ValueError("Suite must include navigator and shared contract")
        release = {"schema_version": SCHEMA_VERSION, "contract_version": contract_version,
                   "runtime_profile": runtime_profile,
                   "release_id": release_id, "status": "candidate", "files": files,
                   "validation_receipts": list(validation_receipts)}
        release["bundle_digest"] = _digest(release)
        _validate_metadata(release, root)
        return release

    if apply:
        # Keep the builder lock outside the inventory to avoid hashing its own lock.
        with exclusive_lock(root.parent / ("." + root.name + ".workflow-release")):
            release = candidate()
            if _inventory(root) != release["files"]:
                raise ValueError("Packaged files changed while building the candidate")
            _atomic_json(metadata_path, release)
    else:
        release = candidate()
    return {"schema_version": SCHEMA_VERSION, "status": "candidate", "applied": bool(apply),
            "metadata_path": str(metadata_path), "runtime_profile": runtime_profile, "release": release}


def inspect_release(skills_dir, validation_receipts=()):
    """Rehash every packaged file and check explicitly supplied receipt declarations."""
    root = _directory(skills_dir)
    release = _read_json(_relative(root, RELEASE_PATH))
    _validate_metadata(release, root)
    # A personal installation also contains unrelated user/system skills.
    # Inspect every file inside the declared packages, never those other skills.
    package_roots = {name.split("/", 1)[0] for name in release["files"]}
    actual = _inventory(root, package_roots)
    if actual != release["files"]:
        changed = sorted(name for name in set(actual) | set(release["files"])
                         if actual.get(name) != release["files"].get(name))
        raise ValueError("Packaged release differs from its hashes: " + ", ".join(changed))
    if ROUTING_PATH not in release["files"]:
        raise ValueError("Release runtime_profile requires a content-bound model-routing.json")
    validate_runtime_profile(root, _release_profile(release), legacy_release=release)
    receipts = []
    for reference in validation_receipts:
        receipt_path = _checked_path(reference)
        if receipt_path.is_relative_to(root):
            raise ValueError("Validation receipts must be outside the digested suite")
        receipt = _read_json(receipt_path)
        if (type(receipt.get("schema_version")) is not int or receipt["schema_version"] != SCHEMA_VERSION
                or not isinstance(receipt.get("receipt_id"), str) or not receipt["receipt_id"].strip()
                or receipt.get("bundle_digest") != release["bundle_digest"]
                or receipt.get("scope") != "workflow-release" or receipt.get("status") != "passed"):
            raise ValueError(f"Receipt must declare a passed workflow-release scope for this digest: {receipt_path}")
        evidence = _references(receipt.get("evidence_refs"), "evidence_refs")
        if not evidence:
            raise ValueError("Validation receipt must name actual validation evidence")
        receipts.append({"path": str(receipt_path), "receipt_id": receipt["receipt_id"],
                         "sha256": hashlib.sha256(_canonical(receipt)).hexdigest(),
                         "scope": receipt["scope"], "status": receipt["status"],
                         "bundle_digest": receipt["bundle_digest"], "evidence_refs": evidence})
    validation = {"accepted": bool(receipts), "receipts": receipts, "trust": TRUST}
    return {"schema_version": SCHEMA_VERSION, "status": "verified" if receipts else "candidate",
            "runtime_profile": _release_profile(release), "release": release, "validation": validation}


def _select_state(project, state):
    if state is not None:
        path = _relative(project, state)
        if not path.is_file():
            raise ValueError(f"Designated state must already exist: {path}")
        return path, "designated"
    found = []
    for relative in DESIGNATED_STATES:
        path = _relative(project, relative)
        if path.exists():
            if not path.is_file():
                raise ValueError(f"Designated state is not a JSON file: {path}")
            found.append(path)
    if len(found) > 1:
        raise ValueError("Multiple designated state files; select one with --state")
    if found:
        return found[0], "designated"
    return _relative(project, ".research/workflow.json"), "fallback"


def _project_record(path):
    record = _read_json(path) if path.exists() else {}
    workflow = record.get("workflow", {})
    if not isinstance(workflow, dict):
        raise ValueError("Existing workflow field is not an object; provide a supported adapter")
    if not isinstance(workflow.get("upgrade_history", []), list):
        raise ValueError("Existing workflow.upgrade_history must be a list")
    if not isinstance(workflow.get("running_job_pins", {}), dict):
        raise ValueError("Existing workflow.running_job_pins must be an object")
    copy_pins = workflow.get("local_copy_pins", {})
    if not isinstance(copy_pins, dict):
        raise ValueError("Existing workflow.local_copy_pins must be an object")
    for relative, pin in copy_pins.items():
        if not isinstance(pin, dict):
            raise ValueError("Local copy pins must be objects")
        _relative(path.parent, relative)
        _file_hashes(pin.get("files"), path.parent)
    previous = workflow.get("adopted_release")
    if previous is not None:
        if not isinstance(previous, dict):
            raise ValueError("Existing adopted_release must be a release object")
        _validate_metadata(previous, path.parent)
    if "runtime_profile" in workflow:
        bound_profile = _profile(workflow["runtime_profile"])
        if previous and bound_profile != _release_profile(previous):
            raise ValueError("Project runtime_profile disagrees with adopted_release")
    return record, workflow, previous


def _local_copies(project, release, previous, workflow, local_skills):
    roots = list(LOCAL_SKILLS)
    if local_skills is not None:
        roots.append(os.fspath(local_skills))
    baseline = previous["files"] if previous else release["files"]
    copies, conflicts = [], []
    seen = set()
    for relative in roots:
        root = _relative(project, relative)
        if root in seen or not root.exists():
            continue
        seen.add(root)
        if not root.is_dir():
            raise ValueError(f"Local skills root is not a directory: {root}")
        for folder in sorted(root.iterdir()):
            if not folder.name.startswith("research-"):
                continue
            _checked_path(folder)
            if not folder.is_dir():
                raise ValueError(f"Local research skill is not a directory: {folder}")
            actual = {folder.name + "/" + name: digest for name, digest in _inventory(folder).items()
                      if folder.name + "/" + name != RELEASE_PATH}
            expected = {name: digest for name, digest in baseline.items()
                        if name.startswith(folder.name + "/")}
            target = {name: digest for name, digest in release["files"].items()
                      if name.startswith(folder.name + "/")}
            local_relative = folder.relative_to(project).as_posix()
            retained = workflow.get("local_copy_pins", {}).get(local_relative)
            if expected and actual == expected:
                status = "matches-previous" if previous else "matches-candidate"
                basis = (previous or release)["bundle_digest"]
            elif target and actual == target:
                status, basis = "matches-candidate", release["bundle_digest"]
            elif retained and actual == retained["files"]:
                status, basis = "matches-retained", retained.get("bundle_digest")
            else:
                status, basis = "customized", None
            comparison = retained["files"] if retained else expected
            changed = sorted(name for name in set(actual) | set(comparison)
                             if actual.get(name) != comparison.get(name)) if status == "customized" else []
            item = {"path": str(folder), "project_relative_path": local_relative,
                    "status": status, "changed_files": changed, "files": actual,
                    "bundle_digest": basis}
            copies.append(item)
            if status == "customized":
                conflicts.append(item)
    return copies, conflicts


def _running_pins(record, workflow):
    pins = deepcopy(workflow.get("running_job_pins", {}))
    jobs = record.get("jobs", [])
    if isinstance(jobs, dict):
        jobs = [dict(job, id=key) for key, job in jobs.items() if isinstance(job, dict)]
    if not isinstance(jobs, list):
        return pins
    for job in jobs:
        if not isinstance(job, dict) or job.get("status") not in (
            "running", "queued", "submitted", "pending", "unknown"
        ):
            continue
        job_id = job.get("id")
        if isinstance(job_id, str) and job_id not in pins:
            versions = {key: deepcopy(value) for key, value in job.items()
                        if key in ("workflow_release", "release_id", "code", "data", "config", "versions")
                        or key.endswith(("_version", "_revision", "_digest"))}
            if versions:
                pins[job_id] = versions
    return pins


def _profile_switch(workflow, source, target, digest, switch_runtime_profile, switch_authority_ref):
    """Accept explicit instruction references only for this exact profile transition."""
    if switch_runtime_profile is not None:
        _profile(switch_runtime_profile)
    if switch_authority_ref is not None:
        _references([switch_authority_ref], "switch_authority_ref")
    if switch_runtime_profile is not None or switch_authority_ref is not None:
        if switch_runtime_profile != target or switch_authority_ref is None:
            return None
        return {"from_runtime_profile": source, "to_runtime_profile": target,
                "bundle_digest": digest, "authority_ref": switch_authority_ref}
    switch = workflow.get("runtime_profile_switch")
    if (not isinstance(switch, dict) or switch.get("from_runtime_profile") != source
            or switch.get("to_runtime_profile") != target or switch.get("bundle_digest") != digest):
        return None
    try:
        _references([switch.get("authority_ref")], "runtime_profile_switch.authority_ref")
    except ValueError:
        return None
    return {key: switch[key] for key in (
        "from_runtime_profile", "to_runtime_profile", "bundle_digest", "authority_ref")}


def _plan_adoption(project, skills_dir, state, validation_receipts, local_skills,
                   switch_runtime_profile=None, switch_authority_ref=None):
    state_path, source = _select_state(project, state)
    suite = _directory(skills_dir)
    if state_path.is_relative_to(suite):
        raise ValueError("Project state must be outside the digested suite")
    record, workflow, previous = _project_record(state_path)
    inspected = inspect_release(suite, validation_receipts)
    release = inspected["release"]
    runtime_profile = inspected["runtime_profile"]
    previous_profile = _release_profile(previous) if previous else workflow.get("runtime_profile")
    switch = _profile_switch(workflow, previous_profile, runtime_profile, release["bundle_digest"],
                             switch_runtime_profile, switch_authority_ref)
    crossing = previous_profile is not None and previous_profile != runtime_profile
    explicit_switch = crossing and switch is not None
    copies, conflicts = _local_copies(project, release, previous, workflow, local_skills)
    authority = workflow.get("automatic_update_authority", {})
    authority_ref = authority.get("reference") if isinstance(authority, dict) else None
    authorized = (isinstance(authority, dict) and authority.get("enabled") is True
                  and isinstance(authority_ref, str) and bool(authority_ref.strip()))
    decisions = []
    if crossing and not explicit_switch:
        decisions.append("runtime-profile-switch")
    if switch_runtime_profile is not None and switch_runtime_profile != runtime_profile:
        decisions.append("runtime-profile-switch-target")
    if not authorized and not explicit_switch:
        decisions.append("automatic-update-authority")
    if explicit_switch:
        authority_ref = switch["authority_ref"]
    if previous:
        before, after = _version(previous["contract_version"]), _version(release["contract_version"])
        if before[0] != after[0] or after < before:
            decisions.append("incompatible-contract")
        if previous["release_id"] == release["release_id"] and previous["bundle_digest"] != release["bundle_digest"]:
            decisions.append("release-id-reused")
    same = previous is not None and previous["bundle_digest"] == release["bundle_digest"]
    if conflicts:
        status = "conflict"
    elif not inspected["validation"]["accepted"]:
        status = "validation-needed"
    elif same:
        status = "already-adopted"
    elif decisions:
        status = "decision-needed"
    else:
        status = "ready"
    proposed = deepcopy(record)
    pins = _running_pins(record, workflow)
    if status == "ready":
        updated = proposed.setdefault("workflow", {})
        updated["runtime_profile"] = runtime_profile
        updated["adopted_release"] = deepcopy(release)
        updated["previous_release"] = deepcopy(previous)
        updated["running_job_pins"] = pins
        if copies:
            copy_pins = updated.setdefault("local_copy_pins", {})
            for item in copies:
                pin = copy_pins.setdefault(item["project_relative_path"], {})
                pin.update(files=deepcopy(item["files"]), bundle_digest=item["bundle_digest"])
        updated.setdefault("upgrade_history", []).append({
            "adopted_at": datetime.now(timezone.utc).isoformat(),
            "from_release": previous["release_id"] if previous else None,
            "from_runtime_profile": previous_profile, "runtime_profile": runtime_profile,
            "to_runtime_profile": runtime_profile,
            "to_release": release["release_id"], "bundle_digest": release["bundle_digest"],
            "authority_ref": authority_ref, "validation": deepcopy(inspected["validation"]),
        })
        if explicit_switch:
            updated["upgrade_history"][-1]["runtime_profile_switch"] = deepcopy(switch)
            updated.pop("runtime_profile_switch", None)
    return {"schema_version": SCHEMA_VERSION, "status": status, "applied": False,
            "runtime_profile": runtime_profile, "previous_runtime_profile": previous_profile,
            "project": str(project), "state_path": str(state_path), "state_source": source,
            "release": release, "previous_release": previous, "validation": inspected["validation"],
            "decisions": decisions, "conflicts": conflicts, "local_copies": copies,
            "running_job_pins": pins, "record": proposed}


def inspect_project(project, skills_dir, state=None, validation_receipts=(), local_skills=None,
                    switch_runtime_profile=None, switch_authority_ref=None):
    """Read-only adoption plan. Pass an explicit existing JSON state when designated."""
    return _plan_adoption(_directory(project), skills_dir, state, validation_receipts, local_skills,
                          switch_runtime_profile, switch_authority_ref)


def adopt_project(project, skills_dir, state=None, validation_receipts=(), local_skills=None, apply=False,
                  switch_runtime_profile=None, switch_authority_ref=None):
    """Adopt only a validated compatible candidate under existing recorded authority."""
    project = _directory(project)
    if not apply:
        return _plan_adoption(project, skills_dir, state, validation_receipts, local_skills,
                              switch_runtime_profile, switch_authority_ref)
    initial = _plan_adoption(project, skills_dir, state, validation_receipts, local_skills,
                             switch_runtime_profile, switch_authority_ref)
    if initial["status"] != "ready":
        return initial
    path = Path(initial["state_path"])
    path.parent.mkdir(parents=True, exist_ok=True)
    _checked_path(path.parent)
    with exclusive_lock(path):
        result = _plan_adoption(project, skills_dir, state, validation_receipts, local_skills,
                                switch_runtime_profile, switch_authority_ref)
        if result["state_path"] != str(path):
            raise ValueError("Project state designation changed; inspect and retry")
        if result["status"] == "ready":
            _atomic_json(path, result["record"])
            result["status"], result["applied"] = "adopted", True
        return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build-release", help="Build candidate metadata, never a validation receipt")
    build.add_argument("--skills-dir", type=Path, required=True)
    build.add_argument("--release-id", required=True)
    build.add_argument("--contract-version", required=True)
    build.add_argument("--runtime-profile", choices=RUNTIME_PROFILES, required=True)
    build.add_argument("--receipt-ref", action="append", default=[])
    build.add_argument("--apply", action="store_true")
    release = commands.add_parser("inspect-release", help="Check package hashes and supplied declarations")
    release.add_argument("--skills-dir", type=Path, required=True)
    release.add_argument("--validation", type=Path, action="append", default=[])
    for name in ("inspect-project", "adopt-project"):
        command = commands.add_parser(name)
        command.add_argument("--project", type=Path, required=True)
        command.add_argument("--skills-dir", type=Path, required=True)
        command.add_argument("--state", help="Existing JSON state, relative to project")
        command.add_argument("--local-skills", help="Additional local skills root, relative to project")
        command.add_argument("--validation", type=Path, action="append", default=[])
        command.add_argument("--switch-runtime-profile", choices=RUNTIME_PROFILES,
                             help="Explicit target profile switch; requires switch authority")
        command.add_argument("--switch-authority-ref", help="Actual instruction authorizing this profile switch")
        if name == "adopt-project":
            command.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "build-release":
            result = build_release(args.skills_dir, args.release_id, args.contract_version,
                                   args.receipt_ref, args.apply, runtime_profile=args.runtime_profile)
        elif args.command == "inspect-release":
            result = inspect_release(args.skills_dir, args.validation)
        else:
            function = adopt_project if args.command == "adopt-project" else inspect_project
            kwargs = {"apply": args.apply} if args.command == "adopt-project" else {}
            result = function(args.project, args.skills_dir, state=args.state,
                              validation_receipts=args.validation, local_skills=args.local_skills,
                              switch_runtime_profile=args.switch_runtime_profile,
                              switch_authority_ref=args.switch_authority_ref, **kwargs)
    except (OSError, ValueError) as exc:
        print(json.dumps({"schema_version": SCHEMA_VERSION, "status": "error", "error": str(exc)}), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 2 if result["status"] in ("conflict", "validation-needed", "decision-needed") else 0


if __name__ == "__main__":
    raise SystemExit(main())

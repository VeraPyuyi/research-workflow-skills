"""Optional standalone Jev System One adapter. Environment credentials only at execute.

Wire schemas verified against docs.typesafe.ai on 2026-10-24. See
../references/decision-support.md for the local packet and accounting contract.
"""

import argparse
from contextlib import contextmanager
import copy
from fractions import Fraction
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import urllib.error
import urllib.request


ENDPOINT = "https://api.typesafe.ai/v1/systemone"
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
MODEL_ID = re.compile(r"jev-[A-Za-z0-9][A-Za-z0-9._+-]*\Z")
KNOWN_ALIASES = {"jev-latest", "jev-preview"}
STAGES = {
    "research-navigate", "research-scope", "research-survey", "research-ideate",
    "research-design", "research-baseline", "research-implement",
    "research-experiment", "research-analyze", "research-write", "research-review",
    "research-submit", "research-product-discover", "research-product-build",
    "research-product-maintain", "research-product-release", "research-optimize",
}


class Invalid(ValueError):
    """Only fixed, adapter-owned error codes may cross the boundary."""


def require(condition, code):
    if not condition:
        raise Invalid(code)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def number(value, minimum=0, maximum=None):
    return (type(value) in (int, float) and math.isfinite(value)
            and value >= minimum and (maximum is None or value <= maximum))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def fingerprint(value):
    return hashlib.sha256(canonical(value).encode("ascii")).hexdigest()


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate_json_key")
        result[key] = value
    return result


def _bad_constant(value):
    raise Invalid("nonfinite_json")


def decode_json(value):
    return json.loads(value, object_pairs_hook=_unique_object, parse_constant=_bad_constant)


def fields(value, required, optional=()):
    require(isinstance(value, dict), "invalid_object")
    require(set(required).issubset(value) and set(value) <= set(required) | set(optional),
            "invalid_fields")


def content(value):
    # The documented top-level content union is string | object | array.
    return ((text(value) or isinstance(value, (dict, list))) and bool(value))


def model_name(value):
    return isinstance(value, str) and len(value) <= 128 and MODEL_ID.fullmatch(value) is not None


def validate_served_model_evidence(evidence):
    fields(evidence, {"revision", "reference", "verified", "allowed_versions"})
    require(text(evidence["revision"]) and text(evidence["reference"])
            and evidence["verified"] is True, "unverified_served_model_evidence")
    versions = evidence["allowed_versions"]
    require(isinstance(versions, list) and bool(versions) and all(model_name(v) for v in versions)
            and not KNOWN_ALIASES.intersection(versions) and len(set(versions)) == len(versions),
            "invalid_allowed_served_versions")
    return versions


def validate_packet(packet):
    """Validate local declarations and return only the documented wire body."""
    fields(packet, {"schema_version", "id", "stage", "purpose", "evidence", "candidates",
                    "criteria_revision", "account_supported_models", "abstention_options",
                    "request", "authorization", "cost_reservation", "served_model_evidence"}, {"optimization_budget", "dispatch_snapshot"})
    require(type(packet["schema_version"]) is int and packet["schema_version"] == 1,
            "unsupported_packet_version")
    require(text(packet["id"]) and packet["stage"] in STAGES, "invalid_identity_or_stage")
    require(packet["purpose"] in ("research", "optimization"), "invalid_purpose")
    require(packet["stage"] != "research-optimize" or packet["purpose"] == "optimization",
            "optimizer_requires_optimization_budget")
    for name in ("evidence", "candidates"):
        fields(packet[name], {"revision", "items"})
        require(text(packet[name]["revision"]) and content(packet[name]["items"]),
                "missing_revision_or_items")
    candidates = packet["candidates"]["items"]
    require(isinstance(candidates, dict) and all(text(k) and content(v) for k, v in candidates.items()),
            "invalid_candidates")
    require(text(packet["criteria_revision"]), "missing_criteria_revision")
    models = packet["account_supported_models"]
    require(isinstance(models, list) and bool(models) and all(model_name(m) for m in models)
            and len(set(models)) == len(models), "invalid_account_models")
    validate_served_model_evidence(packet["served_model_evidence"])
    request = copy.deepcopy(packet["request"])
    fields(request, {"state", "questions"}, {"model"})
    request.setdefault("model", "jev-latest")
    require(model_name(request["model"]) and request["model"] in models, "unsupported_model")
    require(content(request["state"]), "invalid_state")
    questions = request["questions"]
    require(isinstance(questions, dict) and bool(questions), "invalid_questions")
    abstentions = packet["abstention_options"]
    require(isinstance(abstentions, dict), "invalid_abstentions")
    choice_names = set()
    for name, question in questions.items():
        require(text(name), "invalid_question_name")
        fields(question, {"type", "instructions"}, {"criteria"})
        require(content(question["instructions"]), "invalid_instructions")
        kind = question["type"]
        require(kind in ("choice", "score", "noul"), "unsupported_primitive")
        criteria = question.get("criteria")
        if kind == "choice":
            choice_names.add(name)
            require(isinstance(criteria, dict) and len(criteria) >= 3
                    and all(text(k) and (v is None or content(v)) for k, v in criteria.items()),
                    "invalid_choice_criteria")
            abstain = abstentions.get(name)
            require(text(abstain) and abstain in criteria and content(criteria[abstain])
                    and abstain not in candidates, "missing_abstention")
            require(set(criteria) - {abstain} <= set(candidates), "unknown_candidate_option")
        elif kind == "score":
            require(isinstance(criteria, list) and 2 <= len(criteria) <= 10
                    and all(content(v) for v in criteria), "invalid_score_criteria")
        elif criteria is not None:
            fields(criteria, {"true", "false"})
            require(all(content(v) for v in criteria.values()), "invalid_noul_criteria")
    require(set(abstentions) == choice_names, "invalid_abstention_names")
    auth = packet["authorization"]
    fields(auth, {"existing_credit_coverage", "budget_authorized", "coverage_reference", "budget_reference"})
    require(auth["existing_credit_coverage"] is True and auth["budget_authorized"] is True,
            "unconfirmed_credit_or_authorization")
    require(text(auth["coverage_reference"]) and text(auth["budget_reference"]),
            "missing_authorization_reference")
    validate_reservation(packet["cost_reservation"])
    if packet["purpose"] == "optimization":
        validate_optimization(packet.get("optimization_budget"), packet["cost_reservation"])
    elif "optimization_budget" in packet:
        raise Invalid("unexpected_optimization_budget")
    # Reject NaN/infinity anywhere, including otherwise opaque structured content.
    canonical(packet)
    return request


def budget_number(value):
    require(number(value), "invalid_budget_number")
    # Exact rational arithmetic avoids rounding a small pending cost to zero.
    return Fraction(str(value))


def validate_reservation(reservation):
    fields(reservation, {"id", "unit", "amount", "approved_limit", "spent", "pending", "recorded", "active"})
    require(text(reservation["id"]) and text(reservation["unit"]) and reservation["recorded"] is True,
            "unrecorded_reservation")
    amount, limit, spent, pending = [budget_number(reservation[k]) for k in ("amount", "approved_limit", "spent", "pending")]
    require(amount > 0 and limit > 0, "nonpositive_reservation_or_limit")
    active = reservation["active"]
    require(isinstance(active, list) and bool(active), "missing_active_reservations")
    seen = {}
    for entry in active:
        fields(entry, {"id", "amount"})
        require(text(entry["id"]) and entry["id"] not in seen, "duplicate_reservation")
        seen[entry["id"]] = budget_number(entry["amount"])
    require(seen.get(reservation["id"]) == amount, "reservation_not_in_active")
    require(spent + pending + sum(seen.values()) <= limit, "credit_budget_exceeded")


def validate_optimization(budget, reservation):
    fields(budget, {"state", "model", "time"})
    require(budget["state"] == "within20", "optimizer_not_within20")
    for dimension in ("model", "time"):
        row = budget[dimension]
        fields(row, {"approved", "spent", "pending", "active", "reservation"})
        values = {k: budget_number(v) for k, v in row.items()}
        require(values["approved"] > 0 and values["reservation"] > 0, "unmeasurable_optimizer_budget")
        if dimension == "model":
            require(values["reservation"] == budget_number(reservation["amount"]),
                    "optimizer_reservation_mismatch")
        require(sum(values[k] for k in ("spent", "pending", "active", "reservation"))
                <= Fraction(1, 5) * values["approved"], "optimizer_budget_exceeded")


def validate_distribution(probabilities, keys):
    require(isinstance(probabilities, dict) and set(probabilities) == set(keys), "invalid_probability_shape")
    require(all(number(v, maximum=1) for v in probabilities.values()), "invalid_probability")
    require(math.isclose(math.fsum(probabilities.values()), 1, rel_tol=0, abs_tol=1e-6),
            "unnormalized_probabilities")


def parse_response(response, request, supported_models, served_model_evidence):
    """Validate without replacing real outputs with prose or a truth threshold."""
    fields(response, {"model", "answers", "usage"})
    allowed_versions = validate_served_model_evidence(served_model_evidence)
    model = response["model"]
    require(model_name(model) and (model in allowed_versions or model in supported_models),
            "unverified_served_model")
    requested = request["model"]
    if requested in allowed_versions:
        require(model == requested, "served_model_mismatch")
    else:
        require(model == requested or model in allowed_versions, "served_model_mismatch")
    answers = response["answers"]
    require(isinstance(answers, dict) and set(answers) == set(request["questions"]), "answer_names_mismatch")
    for name, question in request["questions"].items():
        answer = answers[name]
        kind = question["type"]
        required = {"type", "noul"} if kind == "noul" else {"type", "confidence", "probabilities", kind}
        if kind == "score":
            required.add("legend")
        fields(answer, required)
        require(answer["type"] == kind, "answer_type_mismatch")
        if kind == "noul":
            require(number(answer["noul"], maximum=1), "invalid_noul")
            continue
        require(number(answer["confidence"], maximum=1), "invalid_confidence")
        keys = question["criteria"] if kind == "choice" else [str(i) for i in range(len(question["criteria"]))]
        validate_distribution(answer["probabilities"], keys)
        if kind == "choice":
            choice = answer["choice"]
            require(isinstance(choice, str) and choice in keys, "invalid_selected_choice")
            require(answer["probabilities"][choice] == max(answer["probabilities"].values()),
                    "choice_not_maximum")
        else:
            levels = question["criteria"]
            require(number(answer["score"], maximum=len(levels) - 1), "invalid_score")
            require(answer["legend"] == {str(i): v for i, v in enumerate(levels)}, "score_legend_mismatch")
            mean = math.fsum(int(k) * v for k, v in answer["probabilities"].items())
            require(math.isclose(answer["score"], mean, rel_tol=0, abs_tol=1e-6), "score_mean_mismatch")
    fields(response["usage"], {"input_tokens", "output_tokens"})
    require(all(type(v) is int and v >= 0 for v in response["usage"].values()), "invalid_usage")
    canonical(response)
    return copy.deepcopy(answers), copy.deepcopy(response["usage"]), model


def runtime_config(path=None):
    """Explicit standalone config only; never discover personal/provider files."""
    try:
        config = ({"api_key_env": "TYPESAFE_API_KEY", "models": ["jev-latest"]}
                  if path is None else decode_json(Path(path).read_text(encoding="utf-8")))
        fields(config, {"api_key_env", "models"})
        require(isinstance(config["api_key_env"], str)
                and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", config["api_key_env"]) is not None,
                "invalid_key_environment_reference")
        models = config["models"]
        require(isinstance(models, list) and bool(models) and all(model_name(m) for m in models)
                and len(set(models)) == len(models), "invalid_runtime_models")
        return config
    except Exception:
        raise Invalid("runtime_config_unavailable") from None


def runtime_model(path, requested_model):
    config = runtime_config(path)
    require(requested_model in config["models"], "model_not_in_runtime_whitelist")
    return config


def load_credentials(path, requested_model):
    """Read a single named environment variable; never inline keys or endpoints."""
    try:
        config = runtime_model(path, requested_model)
        key = os.environ.get(config["api_key_env"])
        require(text(key) and key.isascii()
                and not any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in key),
                "missing_or_invalid_runtime_key")
        return key
    except Exception:
        raise Invalid("runtime_credentials_unavailable") from None


def validate_dispatch_snapshot(packet):
    snapshot = packet.get("dispatch_snapshot")
    require(isinstance(snapshot, dict) and snapshot.get("id") == packet["id"],
            "execution_requires_dispatch_snapshot")
    path = Path(__file__).with_name("check_dispatch.py")
    spec = importlib.util.spec_from_file_location("jev_dispatch_guard", path)
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    require(guard.check_decision(snapshot)["status"] == "ready-for-decision",
            "decision_dispatch_not_admitted")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def post_system_one(request, key, timeout):
    """One fixed-host HTTPS POST, no proxies, redirects, cookies or retries."""
    require(number(timeout, minimum=0.001, maximum=120), "invalid_timeout")
    body = canonical(request).encode("ascii")
    req = urllib.request.Request(ENDPOINT, data=body, method="POST", headers={
        "Authorization": "Bearer " + key, "Content-Type": "application/json", "Accept": "application/json",
    })
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    with opener.open(req, timeout=timeout) as result:
        require(result.status == 200, "unexpected_http_status")
        raw = result.read(MAX_RESPONSE_BYTES + 1)
    require(len(raw) <= MAX_RESPONSE_BYTES, "response_too_large")
    return decode_json(raw.decode("utf-8"))


def base_receipt():
    return {
        "schema_version": 1, "execution_status": "blocked", "error_code": None,
        "requested_model": "unknown", "actual_model": "unknown", "actual_model_version": "unknown",
        "outputs": {}, "usage": None, "attempts": 0, "commitment_state": "not_started",
        "cache_reusable": False, "integrator_disposition": "pending",
        "fallback": "native-evidence-comparison", "blocks_research": False,
    }


def redact(value, key):
    # Defensive protection even if a provider echoes a runtime credential.
    if not key:
        return value
    if isinstance(value, str):
        return value.replace(key, "[REDACTED]")
    if isinstance(value, list):
        return [redact(v, key) for v in value]
    if isinstance(value, dict):
        return {redact(k, key): redact(v, key) for k, v in value.items()}
    return value


@contextmanager
def receipt_file(path):
    """One journal per decision, locked through completion; torn writes block."""
    path = Path(path)
    try:
        handle = path.open("x+", encoding="ascii", newline="\n")
    except FileExistsError:
        handle = path.open("r+", encoding="ascii", newline="\n")
    locked = False
    try:
        if os.name == "nt":
            import msvcrt
            # Windows locks are mandatory. Lock beyond content so receipts stay
            # readable by observers while cooperating writers remain serialized.
            handle.seek(2147483647)
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            handle.seek(0)
        else:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        locked = True
        yield handle
    finally:
        if locked:
            handle.seek(0)
            if os.name == "nt":
                handle.seek(2147483647)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


def save_receipt(handle, receipt, key):
    safe = redact(receipt, key)
    encoded = canonical(safe) + "\n"
    handle.seek(0)
    handle.write(encoded)
    handle.truncate()
    handle.flush()
    os.fsync(handle.fileno())
    return safe


def cached_response(prior, request, packet, verified_version):
    require(prior.get("schema_version") == 1 and prior.get("execution_status") == "completed",
            "receipt_not_reusable")
    require(prior.get("packet_fingerprint") == fingerprint(packet), "receipt_packet_mismatch")
    version = prior.get("actual_model_version")
    versions = validate_served_model_evidence(packet["served_model_evidence"])
    require(isinstance(verified_version, str) and verified_version in versions
            and version == verified_version, "current_model_version_not_verified")
    parse_response({"model": version, "answers": prior.get("outputs"), "usage": prior.get("usage")},
                   request, packet["account_supported_models"], packet["served_model_evidence"])
    require(type(prior.get("attempts")) is int and 1 <= prior["attempts"] <= 2,
            "invalid_attempt_history")
    return dict(prior, execution_status="cache_reused", cache_reusable=True, integrator_disposition="pending")


def _execute(packet, request, result, handle, config_path, retry, verified_version, timeout, transport):
    handle.seek(0)
    previous = handle.read()
    prior = decode_json(previous) if previous else None
    if prior is not None:
        require(isinstance(prior, dict) and prior.get("packet_fingerprint") == result["packet_fingerprint"],
                "receipt_packet_mismatch")
        require(type(prior.get("attempts")) is int and 0 <= prior["attempts"] <= 2
                and prior.get("commitment_state") in ("not_started", "pending", "released", "consumed_unreconciled"),
                "invalid_attempt_history")
        result.update(attempts=prior["attempts"], commitment_state=prior["commitment_state"])
        if not retry:
            return cached_response(prior, request, packet, verified_version)
        require(prior.get("execution_status") == "known_failure" and prior.get("commitment_state") == "released"
                and type(prior.get("attempts")) is int and prior["attempts"] == 1,
                "retry_not_permitted")
        result["attempts"] = 1
    else:
        require(not retry, "no_known_failure_to_retry")
    key = load_credentials(config_path, request["model"])
    safe = redact(result, key)
    result.clear()
    result.update(safe)
    result["attempts"] += 1
    result.update(execution_status="in_flight", commitment_state="pending")
    # Flush before touching the network, and retain this commitment on ambiguity.
    save_receipt(handle, result, key)
    try:
        response = (transport or post_system_one)(request, key, timeout)
        require(redact(response, key) == response, "sensitive_response")
        versions = packet["served_model_evidence"]["allowed_versions"]
        if (isinstance(response, dict) and model_name(response.get("model"))
                and response["model"] in packet["account_supported_models"] + versions):
            actual = response["model"]
            result.update(actual_model=actual, actual_model_version=actual if actual in versions else "unknown")
        outputs, usage, actual_model = parse_response(response, request, packet["account_supported_models"],
                                                    packet["served_model_evidence"])
        result.update(execution_status="completed", outputs=outputs, usage=usage, actual_model=actual_model,
                      actual_model_version=actual_model if actual_model in versions else "unknown",
                      commitment_state="consumed_unreconciled", fallback=None)
        # A concrete version is eligible only after explicit verification at reuse.
        result["cache_reusable"] = False
    except urllib.error.HTTPError as error:
        code = error.code
        # Explicit rejection codes establish failure. Server/redirect ambiguity does not.
        known = code in (400, 401, 403, 404, 405, 413, 415, 422, 429)
        result.update(execution_status="known_failure" if known else "completion_unknown",
                      error_code="rate_limited" if code == 429 else "http_rejected" if known else "http_completion_unknown",
                      commitment_state="released" if known else "pending")
        error.close()
    except (Invalid, json.JSONDecodeError, UnicodeError, TypeError, ValueError, OverflowError):
        result.update(execution_status="invalid_response", error_code="invalid_response", commitment_state="pending")
    except Exception:
        # Never log exception strings: they can contain headers, keys or bodies.
        result.update(execution_status="completion_unknown", error_code="network_completion_unknown", commitment_state="pending")
    return save_receipt(handle, result, key)


def decide(packet, *, execute=False, config_path=None, receipt_path=None, retry=False,
           verified_model_version=None, timeout=30, transport=None):
    """Return sanitized JSON data. Dry-run is offline; execute journals one POST.

    transport(request, key, timeout) is an injectable boundary for offline tests.
    No retry is performed implicitly. Do not delete receipts to repeat decisions.
    """
    result = base_receipt()
    try:
        require(type(execute) is bool and type(retry) is bool, "invalid_execution_flags")
        require(number(timeout, minimum=0.001, maximum=120), "invalid_timeout")
        request = validate_packet(packet)
        runtime_model(config_path, request["model"])
        result.update(
            id=packet["id"], stage=packet["stage"], purpose=packet["purpose"], requested_model=request["model"],
            packet_fingerprint=fingerprint(packet), request_fingerprint=fingerprint(request),
            evidence_fingerprint=fingerprint(packet["evidence"]),
            candidate_fingerprint=fingerprint(packet["candidates"]),
            served_model_evidence_fingerprint=fingerprint(packet["served_model_evidence"]),
            criteria_fingerprint=fingerprint({"revision": packet["criteria_revision"], "questions": request["questions"],
                                              "abstention_options": packet["abstention_options"]}),
            reservation={"id": packet["cost_reservation"]["id"], "amount": packet["cost_reservation"]["amount"],
                         "unit": packet["cost_reservation"]["unit"]},
        )
        if not execute:
            require(not retry and verified_model_version is None, "execute_required")
            result["execution_status"] = "dry_run"
            if receipt_path is not None:
                # Dry-run can create a receipt but must never overwrite a journal.
                with Path(receipt_path).open("x", encoding="ascii", newline="\n") as handle:
                    save_receipt(handle, result, None)
            return result
        require(receipt_path is not None, "execution_requires_receipt")
        validate_dispatch_snapshot(packet)
        with receipt_file(receipt_path) as handle:
            return _execute(packet, request, result, handle, config_path, retry,
                            verified_model_version, timeout, transport)
    except Invalid as error:
        result.update(execution_status="blocked", error_code=error.args[0])
    except Exception:
        result.update(execution_status="blocked", error_code="invalid_input_or_receipt_unavailable")
    return result


class SafeArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        # Do not echo raw argv: an unsupported key flag might include a secret.
        raise Invalid("invalid_cli_arguments")


def main(argv=None):
    parser = SafeArgumentParser(description="Advisory Jev Choice/Score/Noul; offline dry-run by default.")
    parser.add_argument("packet", type=Path, help="Local decision packet JSON")
    parser.add_argument("--execute", action="store_true", help="Explicitly authorize one HTTPS POST")
    parser.add_argument("--config", type=Path, help="Explicit JSON with api_key_env and models; no inline key")
    parser.add_argument("--receipt", type=Path, help="Durable per-decision receipt; required for execute")
    parser.add_argument("--retry", action="store_true", help="Explicit second attempt after recorded known failure")
    parser.add_argument("--verified-model-version", help="Currently verified concrete model version for cache reuse")
    parser.add_argument("--timeout", type=float, default=30, help="Socket timeout seconds, 0.001 through 120 (default 30)")
    try:
        args = parser.parse_args(argv)
    except Invalid:
        print(canonical(dict(base_receipt(), error_code="invalid_cli_arguments")))
        return 2
    try:
        packet = decode_json(args.packet.read_text(encoding="utf-8"))
        result = decide(packet, execute=args.execute, config_path=args.config,
                        receipt_path=args.receipt, retry=args.retry,
                        verified_model_version=args.verified_model_version, timeout=args.timeout)
    except Exception:
        result = dict(base_receipt(), error_code="invalid_packet_file")
    print(canonical(result))
    return 0 if result["execution_status"] in ("dry_run", "completed", "cache_reused") else 2


if __name__ == "__main__":
    raise SystemExit(main())

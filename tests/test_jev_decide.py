"""Offline Jev boundary tests. All provider material below is fake."""

import importlib.util
import io
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest import mock
import urllib.error
import uuid


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/research-navigate/scripts/jev_decide.py"
spec = importlib.util.spec_from_file_location("jev_decide", SCRIPT)
jev = importlib.util.module_from_spec(spec) if SCRIPT.exists() else None
if jev is not None:
    spec.loader.exec_module(jev)


def packet():
    return {
        "schema_version": 1,
        "id": "decision-1",
        "stage": "research-ideate",
        "purpose": "research",
        "evidence": {"revision": "e1", "items": ["Supplied artifact A"]},
        "candidates": {"revision": "c1", "items": {"a": "Method A", "b": "Method B"}},
        "criteria_revision": "r1",
        "account_supported_models": ["jev-latest", "jev-preview"],
        "served_model_evidence": {
            "revision": "served-v1", "reference": "supplied-version-evidence",
            "verified": True, "allowed_versions": ["jev-1.13.0", "jev-1.14.0"],
        },
        "abstention_options": {"compare": "insufficient_evidence"},
        "request": {
            "state": {"evidence": "Artifact A", "candidates": ["Method A", "Method B"]},
            "questions": {
                "compare": {
                    "type": "choice", "instructions": "Which method merits further inspection?",
                    "criteria": {"a": "Inspect A", "b": "Inspect B",
                                 "insufficient_evidence": "Decline: insufficient evidence"},
                },
                "quality": {"type": "score", "instructions": "Rate evidence completeness",
                            "criteria": ["Missing", "Partial", "Complete"]},
                "relevant": {"type": "noul", "instructions": "Is A relevant?",
                             "criteria": {"true": "Direct evidence", "false": "No direct evidence"}},
            },
        },
        "authorization": {
            "existing_credit_coverage": True, "budget_authorized": True,
            "coverage_reference": "existing-allocation-1", "budget_reference": "approval-1",
        },
        "cost_reservation": {
            "id": "reserve-1", "unit": "credits", "amount": 1,
            "approved_limit": 100, "spent": 10, "pending": 2, "recorded": True,
            "active": [{"id": "reserve-1", "amount": 1}],
        },
    }


def response():
    return {
        "model": "jev-1.13.0",
        "answers": {
            "compare": {"type": "choice", "choice": "a", "confidence": 0.6,
                        "probabilities": {"a": 0.7, "b": 0.2, "insufficient_evidence": 0.1}},
            "quality": {"type": "score", "score": 1.43, "confidence": 0.35,
                        "legend": {"0": "Missing", "1": "Partial", "2": "Complete"},
                        "probabilities": {"0": 0.0, "1": 0.57, "2": 0.43}},
            "relevant": {"type": "noul", "noul": 0.93},
        },
        "usage": {"input_tokens": 360, "output_tokens": 39},
    }


class TemporaryFiles:
    """Use the writable temp root; some Windows sandboxes deny child dirs."""

    def __init__(self):
        self.prefix = "jev-offline-" + uuid.uuid4().hex + "-"
        self.paths = set()

    def __truediv__(self, name):
        path = Path(tempfile.gettempdir()) / (self.prefix + name)
        self.paths.add(path)
        return path

    def cleanup(self):
        for path in self.paths:
            path.unlink(missing_ok=True)


class JevTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(jev, "native Jev adapter has not been implemented")
        self.base = TemporaryFiles()
        self.addCleanup(self.base.cleanup)
        self.providers = self.base / "providers.json"
        self.providers.write_text(json.dumps({"providers": [{
            "id": "typesafe", "key": "FAKE-SECRET-DO-NOT-LOG",
            "models": ["jev-latest", "jev-preview", "jev-1.13.0", "jev-1.14.0"],
            "baseUrl": "https://untrusted.invalid",
        }]}), encoding="ascii")
        self.receipt = self.base / "receipt.json"
        self.addCleanup(mock.patch.stopall)
        mock.patch.object(socket, "create_connection", side_effect=AssertionError("real network forbidden")).start()
        mock.patch.object(socket.socket, "connect", side_effect=AssertionError("real network forbidden")).start()

    def execute(self, p=None, result=None, **kwargs):
        value = response() if result is None else result
        transport = kwargs.pop("transport", lambda request, key, timeout: value)
        return jev.decide(packet() if p is None else p, execute=True,
                          providers_path=self.providers, receipt_path=self.receipt,
                          transport=transport, **kwargs)

    def test_documented_wire_shape_and_default_model(self):
        p = packet()
        seen = []
        def send(request, key, timeout):
            seen.append((request, key, timeout))
            return response()
        r = self.execute(p, transport=send)
        self.assertEqual(r["execution_status"], "completed")
        self.assertEqual(seen[0][0], {"model": "jev-latest", **p["request"]})
        self.assertEqual(set(seen[0][0]), {"model", "state", "questions"})
        self.assertEqual(seen[0][1], "FAKE-SECRET-DO-NOT-LOG")
        self.assertEqual(seen[0][2], 30)

    def test_dry_run_never_opens_credentials_or_network(self):
        with mock.patch.object(jev, "load_credentials", side_effect=AssertionError("key access")), \
                mock.patch.object(jev, "post_system_one", side_effect=AssertionError("network")):
            r = jev.decide(packet())
        self.assertEqual(r["execution_status"], "dry_run")
        self.assertEqual(r["actual_model"], "unknown")
        self.assertEqual(r["attempts"], 0)

    def test_choice_decline_is_a_real_preserved_option(self):
        res = response()
        res["answers"]["compare"].update(choice="insufficient_evidence", confidence=1.0,
                                        probabilities={"a": 0, "b": 0, "insufficient_evidence": 1})
        r = self.execute(result=res)
        self.assertEqual(r["outputs"], res["answers"])
        self.assertEqual(r["integrator_disposition"], "pending")
        self.assertNotIn("rationale", r)
        self.assertNotIn("conclusion", r)

    def test_multiple_abstentions_are_local_choice_options(self):
        p = packet()
        p["abstention_options"]["compare"] = [
            "insufficient_evidence",
            "none_suitable",
            "retain_current_model",
        ]
        p["request"]["questions"]["compare"]["criteria"].update({
            "none_suitable": "No candidate is suitable",
            "retain_current_model": "Keep the current model",
        })
        result = jev.decide(p)
        self.assertEqual(result["execution_status"], "dry_run")
        self.assertNotIn("none_suitable", p["candidates"]["items"])

    def test_preserves_all_raw_primitive_outputs_and_usage(self):
        r = self.execute()
        self.assertEqual(r["outputs"], response()["answers"])
        self.assertEqual(r["usage"], {"input_tokens": 360, "output_tokens": 39})
        self.assertEqual(r["requested_model"], "jev-latest")
        self.assertEqual(r["actual_model_version"], "jev-1.13.0")
        self.assertEqual(json.loads(self.receipt.read_text())["outputs"], response()["answers"])
        for field in ("packet_fingerprint", "request_fingerprint", "evidence_fingerprint", "criteria_fingerprint"):
            self.assertEqual(len(r[field]), 64)

    def test_rejects_guessed_question_types_shapes_and_effort(self):
        mutations = [
            lambda p: p["request"].update(effort="high"),
            lambda p: p.update(effort="high"),
            lambda p: p["request"]["questions"]["relevant"].update(type="boolean"),
            lambda p: p["request"]["questions"]["quality"].update(criteria={"0": "Low", "1": "High"}),
            lambda p: p["request"]["questions"]["quality"].update(criteria=["Only one"]),
            lambda p: p["request"]["questions"]["quality"].update(criteria=["Level"] * 11),
            lambda p: p["request"]["questions"]["compare"].update(criteria=["a", "b"]),
            lambda p: p["request"]["questions"]["compare"]["criteria"].pop("insufficient_evidence"),
            lambda p: p["abstention_options"].clear(),
            lambda p: p["request"]["questions"]["relevant"].update(criteria={"yes": "Yes", "no": "No"}),
            lambda p: p["request"].update(state=True),
            lambda p: p["request"]["questions"]["relevant"].update(instructions=123),
        ]
        for mutate in mutations:
            p = packet()
            mutate(p)
            with self.subTest(mutation=mutate):
                self.assertEqual(jev.decide(p)["execution_status"], "blocked")

    def test_structured_instructions_and_optional_noul_criteria(self):
        p = packet()
        p["request"]["questions"]["relevant"].pop("criteria")
        p["request"]["questions"]["relevant"]["instructions"] = {"question": ["Is A relevant?"]}
        self.assertEqual(jev.decide(p)["execution_status"], "dry_run")

    def test_strict_authorization_never_accepts_truthy_or_unknown(self):
        for field in ("existing_credit_coverage", "budget_authorized"):
            for value in (False, 0, 1, "true", "unknown", None, float("nan")):
                p = packet()
                p["authorization"][field] = value
                with self.subTest(field=field, value=value):
                    self.assertEqual(jev.decide(p)["execution_status"], "blocked")
        p = packet()
        p["cost_reservation"]["recorded"] = 1
        self.assertEqual(jev.decide(p)["execution_status"], "blocked")

    def test_pending_and_all_active_reservations_count_against_credit(self):
        p = packet()
        p["cost_reservation"].update(approved_limit=13, active=[
            {"id": "reserve-1", "amount": 1}, {"id": "other", "amount": 1}])
        self.assertEqual(jev.decide(p)["execution_status"], "blocked")
        p["cost_reservation"]["approved_limit"] = 14
        self.assertEqual(jev.decide(p)["execution_status"], "dry_run")

    def test_invalid_reservation_numbers_identity_and_duplicates_block(self):
        for field in ("amount", "approved_limit", "spent", "pending"):
            for value in (True, False, -1, float("nan"), float("inf"), "unknown", None):
                p = packet()
                p["cost_reservation"][field] = value
                with self.subTest(field=field, value=value):
                    self.assertEqual(jev.decide(p)["execution_status"], "blocked")
        for active in ([], [{"id": "reserve-1", "amount": 2}],
                       [{"id": "reserve-1", "amount": 1}] * 2):
            p = packet()
            p["cost_reservation"]["active"] = active
            self.assertEqual(jev.decide(p)["execution_status"], "blocked")

    def test_optimization_requires_within20_and_measurable_both_budgets(self):
        p = packet()
        p["stage"] = "research-optimize"
        p["purpose"] = "optimization"
        self.assertEqual(jev.decide(p)["execution_status"], "blocked")
        p["optimization_budget"] = {
            "state": "within20", "model": {"approved": 100, "spent": 10, "pending": 5, "active": 4, "reservation": 1},
            "time": {"approved": 200, "spent": 20, "pending": 10, "active": 5, "reservation": 5},
        }
        self.assertEqual(jev.decide(p)["execution_status"], "dry_run")
        p["optimization_budget"]["model"]["reservation"] = 1.01
        self.assertEqual(jev.decide(p)["execution_status"], "blocked")
        p["optimization_budget"]["model"]["reservation"] = 1
        p["optimization_budget"]["time"]["active"] = True
        self.assertEqual(jev.decide(p)["execution_status"], "blocked")

    def test_optimizer_stage_cannot_mislabel_research_to_skip_its_budget(self):
        p = packet()
        p["stage"] = "research-optimize"
        self.assertEqual(jev.decide(p)["execution_status"], "blocked")
        p["purpose"] = "optimization"
        p["optimization_budget"] = {
            "state": "within20",
            "model": {"approved": 100, "spent": 0, "pending": 0, "active": 0, "reservation": 1},
            "time": {"approved": 100, "spent": 0, "pending": 0, "active": 0, "reservation": 1},
        }
        self.assertEqual(jev.decide(p)["execution_status"], "dry_run")
        p["authorization"]["existing_credit_coverage"] = "unknown"
        self.assertEqual(jev.decide(p)["execution_status"], "blocked")

    def test_malformed_response_is_sanitized_and_retains_commitment(self):
        mutations = [
            lambda r: r["answers"].pop("relevant"),
            lambda r: r["answers"].update(extra={"type": "noul", "noul": 0}),
            lambda r: r["answers"]["compare"].update(choice="not-an-option"),
            lambda r: r["answers"]["compare"].update(choice="b"),
            lambda r: r["answers"]["compare"].update(probabilities={"a": 0.7, "b": 0.2}),
            lambda r: r["answers"]["compare"]["probabilities"].update(a=0.6),
            lambda r: r["answers"]["compare"].update(confidence=True),
            lambda r: r["answers"]["quality"].update(score=3),
            lambda r: r["answers"]["quality"].update(score=1),
            lambda r: r["answers"]["quality"]["legend"].update({"0": "Other"}),
            lambda r: r["answers"]["relevant"].update(noul=True),
            lambda r: r["answers"]["relevant"].update(noul=float("nan")),
            lambda r: r["answers"]["relevant"].update(noul=1.01),
            lambda r: r["usage"].update(input_tokens=True),
            lambda r: r.pop("usage"),
            lambda r: r.update(error="FAKE-SECRET-DO-NOT-LOG provider internal message"),
        ]
        for index, mutate in enumerate(mutations):
            res = response()
            mutate(res)
            with self.subTest(index=index):
                self.receipt = self.base / ("invalid-%s.json" % index)
                r = self.execute(result=res)
                self.assertEqual(r["execution_status"], "invalid_response")
                self.assertEqual(r["commitment_state"], "pending")
                self.assertEqual(r["outputs"], {})
                self.assertNotIn("FAKE-SECRET", json.dumps(r))

    def test_model_identity_missing_alias_wrong_version(self):
        for index, served in enumerate((None, "jev-latest", "other-1", "jev-9.9.9")):
            res = response()
            if served is None:
                res.pop("model")
            else:
                res["model"] = served
            self.receipt = self.base / ("identity-%s.json" % index)
            r = self.execute(result=res)
            self.assertFalse(r["cache_reusable"])
            if served is None:
                self.assertEqual(r["actual_model"], "unknown")
                self.assertEqual(r["execution_status"], "invalid_response")
            elif served == "jev-latest":
                self.assertEqual(r["actual_model_version"], "unknown")
                self.assertEqual(r["execution_status"], "completed")
            else:
                self.assertEqual(r["execution_status"], "invalid_response")
        p = packet()
        p["request"]["model"] = "jev-1.14.0"
        p["account_supported_models"].append("jev-1.14.0")
        self.receipt = self.base / "wrong-pinned.json"
        self.assertEqual(self.execute(p)["execution_status"], "invalid_response")

    def test_cached_reuse_requires_exact_packet_and_current_verified_version(self):
        self.execute()
        fail = lambda *a: self.fail("cache must not make a call")
        r = self.execute(transport=fail, verified_model_version="jev-1.13.0")
        self.assertEqual(r["execution_status"], "cache_reused")
        self.assertEqual(r["attempts"], 1)
        for version in (None, "jev-1.14.0", "jev-latest"):
            self.assertEqual(self.execute(transport=fail, verified_model_version=version)["execution_status"], "blocked")
        p = packet()
        p["evidence"]["revision"] = "e2"
        self.assertEqual(self.execute(p, transport=fail, verified_model_version="jev-1.13.0")["execution_status"], "blocked")

    def test_timeout_unknown_completion_cannot_retry(self):
        r = self.execute(transport=mock.Mock(side_effect=TimeoutError("FAKE-SECRET-DO-NOT-LOG")))
        self.assertEqual(r["execution_status"], "completion_unknown")
        self.assertEqual(r["commitment_state"], "pending")
        self.assertEqual(r["attempts"], 1)
        self.assertNotIn("FAKE-SECRET", self.receipt.read_text())
        blocked = self.execute(retry=True)
        self.assertEqual(blocked["execution_status"], "blocked")
        self.assertEqual(blocked["attempts"], 1)
        self.assertEqual(blocked["commitment_state"], "pending")

    def test_budget_arithmetic_does_not_round_away_small_commitments(self):
        p = packet()
        p["cost_reservation"].update(approved_limit=13, pending=2.0000000000000004)
        self.assertEqual(jev.decide(p)["execution_status"], "blocked")
        p["cost_reservation"].update(approved_limit=13, pending=2,
                                    active=[{"id": "reserve-1", "amount": 1},
                                            {"id": "small", "amount": 1e-30}])
        self.assertEqual(jev.decide(p)["execution_status"], "blocked")

    def test_optimizer_cannot_understate_the_model_reservation(self):
        p = packet()
        p["purpose"] = "optimization"
        p["optimization_budget"] = {
            "state": "within20", "model": {"approved": 100, "spent": 10, "pending": 5, "active": 4, "reservation": 0.5},
            "time": {"approved": 200, "spent": 20, "pending": 10, "active": 5, "reservation": 5},
        }
        self.assertEqual(jev.decide(p)["execution_status"], "blocked")

    def test_valid_served_identity_is_retained_even_on_version_rejection(self):
        p = packet()
        p["request"]["model"] = "jev-1.14.0"
        p["account_supported_models"].append("jev-1.14.0")
        r = self.execute(p)
        self.assertEqual(r["execution_status"], "invalid_response")
        self.assertEqual(r["actual_model"], "jev-1.13.0")
        self.assertEqual(r["actual_model_version"], "jev-1.13.0")

    def test_echoed_key_rejected_even_in_structured_legend(self):
        p = packet()
        key = "FAKE-SECRET-DO-NOT-LOG"
        p["request"]["questions"]["quality"]["criteria"][0] = key
        res = response()
        res["answers"]["quality"]["legend"]["0"] = key
        r = self.execute(p, result=res)
        self.assertEqual(r["execution_status"], "invalid_response")
        self.assertEqual(r["outputs"], {})
        self.assertNotIn(key, self.receipt.read_text())

    def test_json_parser_rejects_duplicate_keys_and_nonfinite(self):
        for source in ('{"id": "a", "id": "b"}', '{"noul": NaN}', '{"noul": Infinity}'):
            with self.subTest(source=source), self.assertRaises(ValueError):
                jev.decode_json(source)

    def test_transport_rejects_missing_large_or_malformed_response(self):
        class Reply:
            status = 200
            def __init__(self, raw):
                self.raw = raw
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self, limit):
                return self.raw[:limit]
        for index, raw in enumerate((b"", b"{bad", b"x" * (2 * 1024 * 1024 + 1))):
            self.receipt = self.base / ("wire-%s.json" % index)
            opener = mock.Mock()
            opener.open.return_value = Reply(raw)
            with mock.patch.object(jev.urllib.request, "build_opener", return_value=opener):
                r = self.execute(transport=jev.post_system_one)
            self.assertEqual(r["execution_status"], "invalid_response")
            self.assertEqual(r["commitment_state"], "pending")

    def test_interrupted_or_corrupt_receipt_never_triggers_a_new_request(self):
        def interrupt(*args):
            raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            self.execute(transport=interrupt)
        before = self.receipt.read_bytes()
        r = self.execute(retry=True)
        self.assertEqual(r["execution_status"], "blocked")
        self.assertEqual(r["commitment_state"], "pending")
        self.assertEqual(before, self.receipt.read_bytes())
        self.receipt.write_text('{"partial":', encoding="ascii")
        fail = lambda *a: self.fail("corrupt journal must block execution")
        self.assertEqual(self.execute(transport=fail)["execution_status"], "blocked")

    def test_execute_requires_receipt_and_rejects_unknown_timeouts(self):
        self.assertEqual(jev.decide(packet(), execute=True, providers_path=self.providers)["execution_status"], "blocked")
        for value in (True, 0, 0.0001, -1, float("nan"), float("inf"), "30", 121):
            with self.subTest(timeout=value):
                self.assertEqual(jev.decide(packet(), timeout=value)["execution_status"], "blocked")

    def test_unknown_credit_blocks_before_runtime_key_or_transport(self):
        p = packet()
        p["authorization"]["existing_credit_coverage"] = "unknown"
        sent = []
        with mock.patch.object(jev, "load_credentials", side_effect=AssertionError("key access")) as credentials:
            r = self.execute(p, transport=lambda *args: sent.append(args))
        self.assertEqual(r["execution_status"], "blocked")
        self.assertEqual(r["error_code"], "unconfirmed_credit_or_authorization")
        credentials.assert_not_called()
        self.assertEqual(sent, [])
        self.assertFalse(self.receipt.exists())

    def test_failed_durable_reservation_save_never_sends(self):
        sent = []
        def send(*args):
            sent.append(args)
            return response()
        with mock.patch.object(jev.os, "fsync", side_effect=OSError("private filesystem message")):
            r = self.execute(transport=send)
        self.assertEqual(r["execution_status"], "blocked")
        self.assertEqual(sent, [])
        self.assertNotIn("private filesystem message", json.dumps(r))

    def test_retry_can_succeed_but_cannot_authorize_a_third_call(self):
        err = urllib.error.HTTPError(jev.ENDPOINT, 429, "private", {}, io.BytesIO(b"private"))
        self.execute(transport=mock.Mock(side_effect=err))
        r = self.execute(retry=True)
        self.assertEqual(r["execution_status"], "completed")
        self.assertEqual(r["attempts"], 2)
        before = self.receipt.read_bytes()
        self.assertEqual(self.execute(retry=True)["execution_status"], "blocked")
        self.assertEqual(before, self.receipt.read_bytes())

    def test_explicit_retry_only_after_known_failure_at_most_once(self):
        error = urllib.error.HTTPError(jev.ENDPOINT, 429, "FAKE-SECRET-DO-NOT-LOG", {}, io.BytesIO(b"private error"))
        r = self.execute(transport=mock.Mock(side_effect=error))
        self.assertEqual(r["execution_status"], "known_failure")
        self.assertEqual(r["error_code"], "rate_limited")
        self.assertEqual(r["commitment_state"], "released")
        self.assertEqual(self.execute()["execution_status"], "blocked")
        r = self.execute(retry=True, transport=mock.Mock(side_effect=error))
        self.assertEqual(r["attempts"], 2)
        self.assertEqual(self.execute(retry=True)["execution_status"], "blocked")
        self.assertNotIn("FAKE-SECRET", self.receipt.read_text())

    def test_commitment_is_durable_before_transport_and_concurrency_blocks(self):
        def send(*args):
            saved = json.loads(self.receipt.read_text())
            self.assertEqual(saved["execution_status"], "in_flight")
            self.assertEqual(saved["commitment_state"], "pending")
            self.assertEqual(saved["attempts"], 1)
            self.assertEqual(self.execute()["execution_status"], "blocked")
            return response()
        self.assertEqual(self.execute(transport=send)["execution_status"], "completed")

    def test_dry_run_does_not_overwrite_execution_receipt(self):
        self.execute()
        before = self.receipt.read_bytes()
        r = jev.decide(packet(), receipt_path=self.receipt)
        self.assertEqual(r["execution_status"], "blocked")
        self.assertEqual(before, self.receipt.read_bytes())

    def test_transport_fixed_host_post_no_redirect_proxy_or_retry(self):
        calls = []
        class Reply:
            status = 200
            def __enter__(self):
                return self
            def __exit__(self, *a):
                return False
            def read(self, limit):
                return json.dumps(response()).encode("ascii")
        class Opener:
            def open(self, request, timeout):
                calls.append((request, timeout))
                return Reply()
        with mock.patch.object(jev.urllib.request, "build_opener", return_value=Opener()) as build:
            r = jev.post_system_one({"model": "jev-latest", **packet()["request"]}, "FAKE", 9)
        self.assertEqual(r, response())
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0].full_url, "https://api.typesafe.ai/v1/systemone")
        self.assertEqual(calls[0][0].method, "POST")
        self.assertEqual(calls[0][1], 9)
        handlers = build.call_args.args
        redirect = next(h for h in handlers if isinstance(h, jev.NoRedirect))
        self.assertIsNone(redirect.redirect_request(None, None, 307, "", {}, "https://evil.invalid"))
        proxy = next(h for h in handlers if isinstance(h, jev.urllib.request.ProxyHandler))
        self.assertEqual(proxy.proxies, {})

    def test_redirects_server_errors_and_invalid_json_are_not_echoed(self):
        for code, status in ((302, "completion_unknown"), (307, "completion_unknown"),
                             (401, "known_failure"), (500, "completion_unknown")):
            self.receipt = self.base / ("http-%s.json" % code)
            err = urllib.error.HTTPError(jev.ENDPOINT, code, "FAKE-SECRET-DO-NOT-LOG", {}, io.BytesIO(b"provider private"))
            r = self.execute(transport=mock.Mock(side_effect=err))
            self.assertEqual(r["execution_status"], status)
            self.assertNotIn("FAKE-SECRET", json.dumps(r))
            self.assertNotIn("provider private", json.dumps(r))
        self.receipt = self.base / "decode.json"
        r = self.execute(transport=mock.Mock(side_effect=json.JSONDecodeError("private", "secret", 0)))
        self.assertEqual(r["execution_status"], "invalid_response")

    def test_runtime_credentials_only_named_provider_and_requested_model(self):
        self.providers.write_text(json.dumps({"providers": [{"id": "other", "key": "FAKE"}]}))
        self.assertEqual(self.execute()["execution_status"], "blocked")
        self.providers.write_text(json.dumps({"providers": [{"id": "typesafe", "key": "FAKE", "models": ["other"]}]}))
        self.assertEqual(self.execute()["execution_status"], "blocked")

    def test_preview_account_alias_accepts_explicit_served_version_evidence(self):
        self.providers.write_text(json.dumps({"providers": [
            {"id": "typesafe", "key": "FAKE-SECRET-DO-NOT-LOG", "models": ["jev-latest"]}
        ]}))
        original = self.providers.read_bytes()
        p = packet()
        p["request"]["model"] = "jev-preview"
        self.assertEqual(self.execute(p)["execution_status"], "blocked")
        self.assertEqual(self.providers.read_bytes(), original)
        # The separately authorized synthetic fixture exposes both aliases.
        self.providers.write_text(json.dumps({"providers": [
            {"id": "typesafe", "key": "FAKE-SECRET-DO-NOT-LOG",
             "models": ["jev-latest", "jev-preview"]}
        ]}))
        original = self.providers.read_bytes()
        self.receipt = self.base / "configured-preview.json"
        r = self.execute(p)
        self.assertEqual(r["execution_status"], "completed")
        self.assertEqual(r["requested_model"], "jev-preview")
        self.assertEqual(r["actual_model_version"], "jev-1.13.0")
        self.assertNotIn("jev-1.13.0", p["account_supported_models"])
        self.assertEqual(self.execute(p, verified_model_version="jev-1.13.0")["execution_status"], "cache_reused")
        self.assertEqual(self.providers.read_bytes(), original)

    def test_served_identity_is_never_derived_from_alias_catalog(self):
        for index, mutate in enumerate((
                lambda p: p.pop("served_model_evidence"),
                lambda p: p["served_model_evidence"].update(verified="unknown"),
                lambda p: p["served_model_evidence"].update(verified=1),
                lambda p: p["served_model_evidence"].update(allowed_versions=["jev-latest"]),
                lambda p: p["served_model_evidence"].update(allowed_versions=["jev-preview"]),
                lambda p: p["served_model_evidence"].update(reference=""))):
            p = packet()
            mutate(p)
            self.assertEqual(jev.decide(p)["execution_status"], "blocked", index)
        p = packet()
        p["served_model_evidence"]["allowed_versions"] = ["jev-1.14.0"]
        self.assertEqual(self.execute(p)["execution_status"], "invalid_response")

    def test_explicit_opaque_served_version_and_evidence_freshness(self):
        p = packet()
        p["served_model_evidence"]["allowed_versions"] = ["jev-build-20261024"]
        res = response()
        res["model"] = "jev-build-20261024"
        r = self.execute(p, result=res)
        self.assertEqual(r["execution_status"], "completed")
        self.assertEqual(r["actual_model_version"], "jev-build-20261024")
        self.assertEqual(self.execute(p, verified_model_version="jev-build-20261024")["execution_status"], "cache_reused")
        p["served_model_evidence"]["revision"] = "served-v2"
        self.assertEqual(self.execute(p, verified_model_version="jev-build-20261024")["execution_status"], "blocked")

    def test_credential_key_canonical_and_unambiguous_legacy_only(self):
        for index, (secrets, expected) in enumerate((
                ({"key": "FAKE-CANONICAL"}, "completed"),
                ({"apiKey": "FAKE-LEGACY"}, "completed"),
                ({"key": "FAKE-SAME", "apiKey": "FAKE-SAME"}, "completed"),
                ({"key": "FAKE-ONE", "apiKey": "FAKE-TWO"}, "blocked"),
                ({"key": "", "apiKey": "FAKE-LEGACY"}, "blocked"))):
            self.receipt = self.base / ("credential-%s.json" % index)
            self.providers.write_text(json.dumps({"providers": [{"id": "typesafe", "models": ["jev-latest"], **secrets}]}))
            r = self.execute()
            self.assertEqual(r["execution_status"], expected)
            self.assertNotIn("FAKE-", json.dumps(r))

    def test_cli_is_dry_by_default_and_emits_sanitized_json(self):
        source = self.base / "packet.json"
        source.write_text(json.dumps(packet()), encoding="ascii")
        output = io.StringIO()
        with mock.patch.object(jev, "load_credentials", side_effect=AssertionError("key access")), \
                mock.patch("sys.stdout", output):
            code = jev.main([str(source)])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output.getvalue())["execution_status"], "dry_run")
        source.write_text('{"x": NaN}', encoding="ascii")
        output = io.StringIO()
        with mock.patch("sys.stdout", output):
            code = jev.main([str(source)])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output.getvalue())["execution_status"], "blocked")


if __name__ == "__main__":
    unittest.main()

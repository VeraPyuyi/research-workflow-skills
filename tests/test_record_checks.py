import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import urllib.error

ROOT = Path(__file__).resolve().parents[1]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


records = load("check_records", "skills/research-navigate/scripts/check_records.py")
refs = load("verify_refs", "skills/research-survey/scripts/verify_refs.py")
claims = load("claim_audit", "skills/research-write/scripts/claim_audit.py")


def jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")


class RecordCheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.p = Path(self.tmp.name)
        base = self.p / "research"
        (base / "protocol").mkdir(parents=True)
        (base / "STATE.json").write_text(json.dumps({"milestone": "M3", "next_action": {}, "coverage": {}}))
        (base / "brief.md").write_text("question")
        (base / "protocol/P1.md").write_text("metric: accuracy")
        (self.p / "eval.py").write_text("def score(): pass\n")
        self.lock = records.lock_protocol(self.p, "research/protocol/P1.md", "user:U1")
        self.evaluator = records.lock_evaluator(self.p, ["eval.py"])
        run = dict(attempt_id="r1", protocol_sha256=self.lock["sha256"], status="completed",
                   data_kind="measured", evaluator_sha256=self.evaluator["digest"])
        jsonl(base / "runs/ledger.jsonl", [run, dict(run, attempt_id="r2", status="failed")])
        self.claim = dict(claim_id="C1", status="supported", run_ids=["r1"], deviations=[],
                          protocol_sha256=self.lock["sha256"], values={"acc": 0.8312})
        jsonl(base / "analysis/claims.jsonl", [self.claim])

    def tearDown(self):
        self.tmp.cleanup()

    def test_consistent_records_pass(self):
        self.assertEqual(records.check(self.p, "M3"), [])

    def test_protocol_and_evaluator_changes_are_detected(self):
        (self.p / "eval.py").write_text("def score(): return 1\n")
        self.assertTrue(any("Evaluator" in x for x in records.check(self.p, "M3")))
        (self.p / "research/protocol/P1.md").write_text("metric: F1")
        self.assertTrue(any("protocol changed" in x for x in records.check(self.p, "M1")))
        with self.assertRaises(ValueError):
            records.lock_protocol(self.p, "research/protocol/P1.md", "user:U1")

    def test_claims_need_completed_measured_runs_and_deviation_lists(self):
        base = self.p / "research/analysis/claims.jsonl"
        for change, expected in ((dict(run_ids=["r2"]), "status failed"),
                                 (dict(run_ids=["missing"]), "unknown run"),
                                 (dict(deviations=None), "deviations"),
                                 (dict(run_ids=[]), "without runs")):
            with self.subTest(change=change):
                jsonl(base, [dict(self.claim, **change)])
                self.assertTrue(any(expected in x for x in records.check(self.p, "M3")))

    def test_synthetic_runs_must_be_declared(self):
        jsonl(self.p / "research/runs/ledger.jsonl",
              [dict(attempt_id="r1", protocol_sha256=self.lock["sha256"], status="completed",
                    data_kind="synthetic", evaluator_sha256=self.evaluator["digest"])])
        self.assertTrue(any("synthetic" in x for x in records.check(self.p, "M3")))

    def test_cited_sources_must_be_resolved(self):
        jsonl(self.p / "research/literature.jsonl",
              [{"id": "a", "read_depth": "full", "verified": "resolved"},
               {"id": "b", "read_depth": "abstract", "verified": "unchecked"}])
        problems = records.check(self.p, "M4", ["a", "b", "c"])
        self.assertTrue(any("b is unchecked" in x for x in problems))
        self.assertTrue(any("c is not in" in x for x in problems))
        tex = self.p / "paper.tex"
        tex.write_text(r"As shown \citep[p.~3]{a, b} and \cite{c}.")
        self.assertEqual(records.cited_keys([tex]), ["a", "b", "c"])


class FakeResolver:
    def __init__(self, table, fail=False):
        self.table, self.fail = table, fail

    def _look(self, key):
        if self.fail:
            raise urllib.error.URLError("offline")
        return self.table.get(key, [])

    def arxiv(self, ident):
        return self._look(ident)

    def doi(self, ident):
        return self._look(ident)

    def title(self, title):
        return self._look(refs.normalize(title))


class VerifyRefsTests(unittest.TestCase):
    BIB = r"""
@article{real, title={Attention Is All You Need}, author={Vaswani, Ashish and Shazeer, Noam},
  journal={arXiv preprint arXiv:1706.03762}, year={2017}}
@inproceedings{doi1, title = {Deep Residual Learning for Image Recognition},
  author = {He, Kaiming and Zhang, Xiangyu}, doi = {10.1109/CVPR.2016.90}}
@article{fake, title={A Plausible but Invented Study of Everything}, author={Doe, Jane}}
@misc{wrong, title={Completely Different Title}, author={Vaswani, Ashish}, eprint={1706.03762},
  archivePrefix={arXiv}}
"""

    def setUp(self):
        hit = [{"title": "Attention is all you need", "authors": ["Ashish Vaswani", "Noam Shazeer"]}]
        self.resolver = FakeResolver({
            "1706.03762": hit,
            "10.1109/CVPR.2016.90": [{"title": "Deep Residual Learning for Image Recognition",
                                      "authors": ["Kaiming He"]}],
        })

    def test_statuses(self):
        entries = refs.parse_bibtex(self.BIB)
        self.assertEqual([e["id"] for e in entries], ["real", "doi1", "fake", "wrong"])
        self.assertEqual(entries[0]["arxiv"], "1706.03762")
        report = refs.run(entries, self.resolver)
        status = {r["id"]: r["status"] for r in report["entries"]}
        self.assertEqual(status, {"real": "resolved", "doi1": "resolved", "fake": "unresolved",
                                  "wrong": "title_mismatch"})
        self.assertFalse(report["passed"])

    def test_network_failure_is_unchecked_not_passed(self):
        report = refs.run(refs.parse_bibtex(self.BIB)[:1], FakeResolver({}, fail=True))
        self.assertEqual(report["entries"][0]["status"], "unchecked")
        self.assertFalse(report["passed"])

    def test_author_mismatch_is_not_resolved(self):
        entry = {"id": "x", "title": "Attention Is All You Need", "authors": ["Someone Else"],
                 "arxiv": "1706.03762"}
        self.assertEqual(refs.verify(entry, self.resolver)["status"], "title_mismatch")


class ClaimAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.p = Path(self.tmp.name)
        jsonl(self.p / "claims.jsonl", [{"claim_id": "C1", "values": {"acc": 0.8312, "gain": 0.042},
                                         "uncertainty": {"type": "ci95", "low": 0.81, "high": 0.85}}])
        (self.p / "table.csv").write_text("method,latency\nours,12.47\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def audit(self, text, **kw):
        tex = self.p / "paper.tex"
        tex.write_text(text, encoding="utf-8")
        return claims.audit([tex], self.p / "claims.jsonl", [self.p / "table.csv"], **kw)

    def test_traced_numbers_pass(self):
        report = self.audit(r"Accuracy reaches 83.1\% (95\% CI 0.81--0.85), a gain of 4.2\%; "
                            r"latency is 12.5 s. See Table 2 and \cite{x2020} (2021).")
        self.assertTrue(report["passed"], report["unmatched"])
        self.assertIsNotNone(report["manuscript_sha256"])

    def test_untraced_number_is_reported_with_line(self):
        report = self.audit("Line one.\nAccuracy reaches 91.7\\% on the test set.")
        self.assertFalse(report["passed"])
        self.assertEqual([(u["text"], u["line"]) for u in report["unmatched"]], [("91.7\\%", 2)])
        self.assertTrue(self.audit("Accuracy reaches 91.7\\%.", allow=["91.7\\%"])["passed"])

    def test_equations_and_labels_are_ignored(self):
        report = self.audit(r"We use $$x = 0.5 y$$ and \label{eq:0.3} with Section 3.2.")
        self.assertEqual(report["numbers_checked"], 0)


if __name__ == "__main__":
    unittest.main()

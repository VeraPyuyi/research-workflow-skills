import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "skills/research-implement/scripts/render_evidence.py"
api = None
if SCRIPT.exists():
    spec = importlib.util.spec_from_file_location("render_evidence", SCRIPT)
    api = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(api)


class PaperArtifactTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(api, "Evidence renderer is not implemented yet")
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.data = self.root / "results.csv"
        self.spec_path = self.root / "figure.json"
        self.spec = {
            "schema_version": 1, "data_kind": "illustrative",
            "data_file": "results.csv", "claim_ids": ["reliability", "conditional-latency"],
            "analysis_revision": "fixture-v1", "width_inches": 3.25,
            "private_note": "/private/author-machine/project",
        }
        self.write_rows([
            ["reference", 20, 16, 15.0],
            ["candidate", 20, 14, 10.0],
        ])
        self.save_spec()

    def save_spec(self):
        self.spec_path.write_text(json.dumps(self.spec), encoding="utf-8")

    def write_rows(self, rows):
        with self.data.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["method", "attempted", "successful", "mean_success_latency_seconds"])
            writer.writerows(rows)

    def test_denominators_failures_order_and_missing_uncertainty_survive(self):
        record = api.load_evidence(self.spec_path)
        self.assertEqual([r["method"] for r in record["rows"]], ["reference", "candidate"])
        self.assertEqual([r["success_rate"] for r in record["rows"]], [0.8, 0.7])
        self.assertEqual([r["failed"] for r in record["rows"]], [4, 6])
        self.assertEqual(record["uncertainty"], "not supplied")
        self.assertEqual(record["latency_population"], "successful attempts only")

    def test_no_success_is_not_zero_latency(self):
        self.write_rows([["reference", 20, 0, ""]])
        record = api.load_evidence(self.spec_path)
        self.assertIsNone(record["rows"][0]["mean_success_latency_seconds"])
        self.assertEqual(record["rows"][0]["failed"], 20)

    def test_missing_success_latency_stays_missing(self):
        self.write_rows([["reference", 20, 16, ""]])
        self.assertIsNone(api.load_evidence(self.spec_path)["rows"][0]["mean_success_latency_seconds"])

    def test_rejects_impossible_or_nonfinite_values(self):
        for row in [
            ["bad", 20, 21, 1], ["bad", -1, 0, ""], ["bad", 2.5, 2, 1],
            ["bad", 20, 16, "NaN"], ["bad", 20, 16, "-1"],
        ]:
            with self.subTest(row=row):
                self.write_rows([row])
                with self.assertRaises(ValueError):
                    api.load_evidence(self.spec_path)

    def test_duplicate_labels_rejected(self):
        self.write_rows([["same", 20, 16, 1], ["same", 20, 15, 2]])
        with self.assertRaises(ValueError):
            api.load_evidence(self.spec_path)

    def test_unknown_kind_rejected_and_private_labels_rejected(self):
        self.spec["data_kind"] = "real-looking"
        self.save_spec()
        with self.assertRaises(ValueError):
            api.load_evidence(self.spec_path)
        self.spec["data_kind"] = "illustrative"
        self.save_spec()
        self.write_rows([["C:\\Users\\author\\secret", 20, 16, 1]])
        with self.assertRaises(ValueError):
            api.load_evidence(self.spec_path)

    def test_empty_or_missing_source_is_pending(self):
        self.write_rows([])
        result = api.render(self.spec_path, self.root / "empty")
        self.assertEqual(result["status"], "pending-data")
        self.assertFalse((self.root / "empty/figure.pdf").exists())
        self.data.unlink()
        result = api.render(self.spec_path, self.root / "missing")
        self.assertEqual(result["status"], "pending-data")

    def test_render_outputs_and_safe_provenance(self):
        result = api.render(self.spec_path, self.root / "output")
        self.assertEqual(result["status"], "rendered")
        for name in [
            "figure.pdf", "figure.svg", "figure.png",
            "table.csv", "table.tex", "table.pdf", "table.png", "provenance.json",
        ]:
            self.assertTrue((self.root / "output" / name).is_file(), name)
        record = json.loads((self.root / "output/provenance.json").read_text())
        self.assertEqual(record["data_kind"], "illustrative")
        self.assertEqual(record["source"]["file"], "results.csv")
        self.assertEqual(len(record["source"]["sha256"]), 64)
        self.assertEqual(record["configuration"]["width_inches"], 3.25)
        self.assertNotIn("private_note", record)
        for name in ["provenance.json", "table.tex", "figure.svg"]:
            text = (self.root / "output" / name).read_text(encoding="utf-8")
            self.assertNotIn("author-machine", text)
            self.assertNotIn(str(self.root), text)
        with (self.root / "output/table.csv").open(encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(rows[1]["failed"], "6")
        self.assertEqual(rows[1]["success_rate"], "0.7")
        self.assertIn("Illustrative", (self.root / "output/figure.svg").read_text())

    def test_source_change_changes_fingerprint_and_repeat_preserves_table(self):
        first = api.render(self.spec_path, self.root / "a")
        second = api.render(self.spec_path, self.root / "b")
        self.assertEqual(first["source"]["sha256"], second["source"]["sha256"])
        self.assertEqual((self.root / "a/table.csv").read_bytes(), (self.root / "b/table.csv").read_bytes())
        self.write_rows([["reference", 20, 15, 15]])
        third = api.load_evidence(self.spec_path)
        self.assertNotEqual(first["source"]["sha256"], third["source"]["sha256"])

    def test_unowned_and_edited_outputs_are_protected(self):
        out = self.root / "unowned"
        out.mkdir()
        (out / "figure.pdf").write_bytes(b"author-owned")
        with self.assertRaises(ValueError):
            api.render(self.spec_path, out)
        self.assertEqual((out / "figure.pdf").read_bytes(), b"author-owned")
        own = self.root / "owned"
        api.render(self.spec_path, own)
        (own / "table.csv").write_bytes(b"author-edited")
        with self.assertRaises(ValueError):
            api.render(self.spec_path, own)
        self.assertEqual((own / "table.csv").read_bytes(), b"author-edited")

    def test_pending_clears_only_verified_generated_outputs(self):
        out = self.root / "owned"
        api.render(self.spec_path, out)
        (out / "notes.txt").write_text("keep")
        self.data.unlink()
        result = api.render(self.spec_path, out)
        self.assertEqual(result["status"], "pending-data")
        self.assertFalse((out / "figure.pdf").exists())
        self.assertEqual((out / "notes.txt").read_text(), "keep")

    def test_invalid_spec_does_not_destroy_valid_outputs(self):
        out = self.root / "owned"
        api.render(self.spec_path, out)
        original = (out / "table.csv").read_bytes()
        self.spec["width_inches"] = -5
        self.save_spec()
        with self.assertRaises(ValueError):
            api.render(self.spec_path, out)
        self.assertEqual((out / "table.csv").read_bytes(), original)

    def test_private_record_fields_and_malformed_csv_are_rejected(self):
        for key, value in [("claim_ids", ["/private/author-machine"]),
                           ("analysis_revision", "C:\\Users\\author\\draft"),
                           ("data_file", "../outside.csv")]:
            with self.subTest(key=key):
                old = self.spec[key]
                self.spec[key] = value
                self.save_spec()
                with self.assertRaises(ValueError):
                    api.load_evidence(self.spec_path)
                self.spec[key] = old
        self.save_spec()
        for body in ["method,attempted,successful,mean_success_latency_seconds\nbad,20\n",
                     "method,attempted,successful,mean_success_latency_seconds\nbad,20,16,3,extra\n"]:
            self.data.write_text(body)
            with self.assertRaises(ValueError):
                api.load_evidence(self.spec_path)


if __name__ == "__main__":
    unittest.main()

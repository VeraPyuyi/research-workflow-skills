"""Reject mismatched versions/categories and leakage between study splits."""

import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "presentation_study", ROOT / "scripts/validate_presentation_study.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


DATA = MODULE.default_data_dir(ROOT)


@unittest.skipUnless((DATA / "discovery-readings.json").is_file(),
                     "study data not fetched; run scripts/fetch_study_data.py")
class StudyIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.library = self.root / "skills/research-write/references/paper-style-study"
        self.docs = self.root / "docs/paper-presentation-study"
        self.library.mkdir(parents=True)
        self.docs.mkdir(parents=True)
        for name in ("sources.json", "patterns.json"):
            shutil.copyfile(ROOT / "skills/research-write/references/paper-style-study" / name,
                            self.library / name)
        for split in ("discovery", "holdout"):
            shutil.copyfile(DATA / f"{split}-readings.json",
                            self.docs / f"{split}-readings.json")
        shutil.copyfile(DATA / "pattern-freeze.json",
                        self.docs / "pattern-freeze.json")

    def change_first_read(self, field, value):
        path = self.docs / "discovery-readings.json"
        data = json.loads(path.read_text("utf-8"))
        data[0][field] = value
        path.write_text(json.dumps(data), "utf-8")

    def test_frozen_study_is_consistent(self):
        self.assertEqual(MODULE.validate_study(self.root, self.docs), [])

    def test_substituted_pdf_version_is_rejected(self):
        self.change_first_read("source_pdf_sha256", "0" * 64)
        self.assertTrue(any("source_pdf_sha256 disagrees" in s
                            for s in MODULE.validate_study(self.root, self.docs)))

    def test_category_relabeling_is_rejected(self):
        self.change_first_read("category", "Invented award")
        self.assertTrue(any("category disagrees" in s
                            for s in MODULE.validate_study(self.root, self.docs)))

    def test_holdout_cannot_become_pattern_discovery_support(self):
        source = json.loads((self.library / "sources.json").read_text("utf-8"))
        withheld = next(p["id"] for p in source["papers"] if p["split"] == "holdout")
        path = self.library / "patterns.json"
        data = json.loads(path.read_text("utf-8"))
        data["cards"][0]["sources"][0]["paper_id"] = withheld
        path.write_text(json.dumps(data), "utf-8")
        self.assertTrue(any("holdout used" in s for s in MODULE.validate_study(self.root, self.docs)))

    def test_unread_locator_is_rejected(self):
        path = self.library / "patterns.json"
        data = json.loads(path.read_text("utf-8"))
        data["cards"][0]["sources"][0]["pdf_pages"] = [10000]
        path.write_text(json.dumps(data), "utf-8")
        self.assertTrue(any("locator exceeds" in s for s in MODULE.validate_study(self.root, self.docs)))

    def test_visual_locator_requires_viewed_detail_page(self):
        path = self.library / "patterns.json"
        data = json.loads(path.read_text("utf-8"))
        source = next(
            item
            for card in data["cards"]
            for item in card["sources"]
            if "figure" in item["locator"].casefold() or "table" in item["locator"].casefold()
        )
        readings = json.loads((self.docs / "discovery-readings.json").read_text("utf-8"))
        record = next(item for item in readings if item["id"] == source["paper_id"])
        nonvisual = sorted(
            set(record["coverage"]["main_pdf_pages_read"])
            - set(record["coverage"]["detail_image_pages_viewed"])
        )
        self.assertTrue(nonvisual)
        source["pdf_pages"] = [nonvisual[0]]
        path.write_text(json.dumps(data), "utf-8")
        self.assertTrue(
            any("visual locator" in error for error in MODULE.validate_study(self.root, self.docs))
        )


if __name__ == "__main__":
    unittest.main()

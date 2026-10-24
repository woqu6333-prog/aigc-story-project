from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from material_library import MaterialLibrary


class Homework5LibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.output = PROJECT_ROOT / "outputs" / "library" / "homework5"
        cls.index = json.loads((cls.output / "index.json").read_text(encoding="utf-8"))
        cls.library = MaterialLibrary(cls.output / "index.json")

    def test_minimum_material_counts(self) -> None:
        self.assertGreaterEqual(self.index["counts"]["template"], 10)
        self.assertGreaterEqual(self.index["counts"]["image"], 20)
        self.assertGreaterEqual(self.index["counts"]["sound"], 5)
        self.assertGreaterEqual(len(self.index["items"]), 59)

    def test_media_files_exist(self) -> None:
        images = list((self.output / "assets" / "images").glob("*.png"))
        sounds = list((self.output / "assets" / "sounds").glob("*.wav"))
        self.assertEqual(len(images), 20)
        self.assertEqual(len(sounds), 5)
        self.assertTrue(all(path.stat().st_size > 5_000 for path in images))
        self.assertTrue(all(path.stat().st_size > 10_000 for path in sounds))

    def test_natural_language_search_returns_relevant_images(self) -> None:
        results = self.library.search("海底鲸鱼保护珊瑚", kind="image", limit=5)
        relevant = sum(bool({"海底", "鲸鱼", "珊瑚", "环保"} & set(result.item["tags"])) for result in results)
        self.assertGreaterEqual(relevant, 4)
        self.assertGreater(results[0].score, 0)

    def test_evaluation_has_three_queries(self) -> None:
        report = json.loads((self.output / "evaluation.json").read_text(encoding="utf-8"))
        self.assertEqual(len(report["cases"]), 3)
        self.assertGreaterEqual(report["average_precision_at_5"], 0.6)
        self.assertEqual(report["backend"], "visual-semantic-fallback")

    def test_library_web_distribution(self) -> None:
        dist = PROJECT_ROOT / "dist" / "library"
        for path in [dist / "index.html", dist / "assets" / "app.js", dist / "data" / "index.json"]:
            with self.subTest(path=path):
                self.assertTrue(path.is_file())


if __name__ == "__main__":
    unittest.main()

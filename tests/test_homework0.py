from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = PROJECT_ROOT / "src" / "web"
DIST_DIR = PROJECT_ROOT / "dist"


class Homework0StaticSiteTests(unittest.TestCase):
    def test_required_source_files_exist(self) -> None:
        required = [
            SOURCE_DIR / "index.html",
            SOURCE_DIR / "assets" / "style.css",
            SOURCE_DIR / "assets" / "app.js",
            PROJECT_ROOT / "README.md",
            PROJECT_ROOT / "docs" / "homework0" / "ai-log.md",
        ]
        for path in required:
            with self.subTest(path=path):
                self.assertTrue(path.is_file(), f"缺少文件：{path}")

    def test_distribution_is_built(self) -> None:
        for relative_path in ["index.html", "assets/style.css", "assets/app.js"]:
            self.assertTrue((DIST_DIR / relative_path).is_file())

    def test_form_contains_required_fields(self) -> None:
        html = (SOURCE_DIR / "index.html").read_text(encoding="utf-8")
        for element_id in ["heroName", "heroAge", "heroInterest", "storyForm"]:
            with self.subTest(element_id=element_id):
                self.assertRegex(html, rf'id="{element_id}"')

    def test_at_least_three_themes_are_available(self) -> None:
        html = (SOURCE_DIR / "index.html").read_text(encoding="utf-8")
        values = re.findall(r'name="theme"\s+value="([a-z]+)"', html)
        self.assertGreaterEqual(len(set(values)), 3)
        self.assertTrue({"courage", "friendship", "nature"}.issubset(values))

    def test_no_remote_runtime_dependency(self) -> None:
        html = (SOURCE_DIR / "index.html").read_text(encoding="utf-8")
        remote_assets = re.findall(r'(?:src|href)="https?://', html)
        self.assertEqual(remote_assets, [], "作业0应当能够完全离线运行")

    def test_javascript_supports_core_actions(self) -> None:
        script = (SOURCE_DIR / "assets" / "app.js").read_text(encoding="utf-8")
        for function_name in ["generateStory", "copyStory", "downloadStory", "validateForm"]:
            with self.subTest(function_name=function_name):
                self.assertIn(f"function {function_name}", script)


if __name__ == "__main__":
    unittest.main()

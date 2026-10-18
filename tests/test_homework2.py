from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from illustration.prompt_builder import CHARACTER_LOCK, build_prompt_manifest
from story_generator.models import StoryOutput


class Homework2PictureBookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.story_path = PROJECT_ROOT / "outputs" / "stories" / "homework2-demo-story.json"
        cls.story_data = json.loads(cls.story_path.read_text(encoding="utf-8"))
        cls.source_dir = PROJECT_ROOT / "src" / "picturebook"

    def test_story_matches_homework1_schema(self) -> None:
        story = StoryOutput.model_validate(self.story_data)
        self.assertEqual(len(story.scenes), 3)
        self.assertEqual([scene.scene_id for scene in story.scenes], [1, 2, 3])

    def test_each_scene_has_an_image(self) -> None:
        image_dir = PROJECT_ROOT / "outputs" / "images" / "homework2"
        self.assertTrue((image_dir / "xiaoyu-character-sheet.png").is_file())
        for scene in self.story_data["scenes"]:
            image = image_dir / f"scene-{scene['scene_id']:02d}.png"
            with self.subTest(image=image):
                self.assertTrue(image.is_file(), f"缺少场景图：{image}")
                self.assertGreater(image.stat().st_size, 100_000, "场景图文件过小")

    def test_prompt_manifest_locks_character_details(self) -> None:
        manifest = build_prompt_manifest(self.story_data)
        self.assertEqual(len(manifest["scenes"]), 3)
        for scene in manifest["scenes"]:
            prompt = scene["prompt"]
            for detail in ["两枚金色月牙发夹", "黄色连帽雨衣", "青绿色小包", "红色雨靴"]:
                with self.subTest(detail=detail):
                    self.assertIn(detail, prompt)
        self.assertIn("每幅图必须保持", CHARACTER_LOCK)

    def test_picturebook_contains_all_pages_and_images(self) -> None:
        html = (self.source_dir / "index.html").read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r'class="book-page[^\"]*"', html)), 6)
        for file_name in [
            "xiaoyu-character-sheet.png",
            "scene-01.png",
            "scene-02.png",
            "scene-03.png",
        ]:
            self.assertIn(file_name, html)

    def test_picturebook_has_no_remote_runtime_dependency(self) -> None:
        html = (self.source_dir / "index.html").read_text(encoding="utf-8")
        self.assertNotRegex(html, r'(?:src|href)="https?://')

    def test_distribution_is_built(self) -> None:
        dist_book = PROJECT_ROOT / "dist" / "picturebook"
        required = [
            dist_book / "index.html",
            dist_book / "assets" / "style.css",
            dist_book / "assets" / "app.js",
            dist_book / "assets" / "images" / "scene-03.png",
            dist_book / "data" / "story.json",
        ]
        for path in required:
            with self.subTest(path=path):
                self.assertTrue(path.is_file(), f"构建产物缺少：{path}")


if __name__ == "__main__":
    unittest.main()
